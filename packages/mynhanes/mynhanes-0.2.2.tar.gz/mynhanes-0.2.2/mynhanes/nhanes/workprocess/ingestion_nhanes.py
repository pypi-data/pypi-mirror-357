import os
import time
from time import sleep
import numpy as np
import pandas as pd
from pathlib import Path
from django.conf import settings
from nhanes.models import WorkProcessNhanes # noqa E501
from nhanes.workprocess import ingestion_utils
from nhanes.utils.logs import logger, start_logger
from core.parameters import config


def ingestion_nhanes(load_type=str('db')):

    # start Log monitor
    log_file = __name__
    v_time_start_process = time.time()
    log = start_logger(log_file)
    logger(log, "s", "Started WorkProcess to Ingestion NHANES Data")

    # check if load_type is valid
    if load_type not in ['db', 'csv', 'both']:
        msm = "Invalid load type. Please choose 'db', 'csv', or 'both'."
        logger(log, "e", msm)
        return False

    # read parameters
    try:
        load_metadata = config['workprocess']['load_metadata']
        if load_metadata is None:
            load_metadata = False
    except KeyError:
        msm = "workprocess.load_metadata key not found on Parameters file."
        logger(log, "e", msm)
        load_metadata = False  # Can be changed to return False

    try:
        download_path = config['workprocess']['download_path']
        if download_path is None:
            download_path = Path(settings.BASE_DIR)
            msm = f"workprocess.download_path key not found on Parameters file. Using {download_path}." # noqa E501
            logger(log, "i", msm)
        else:
            download_path = Path(download_path)
    except KeyError:
        msm = "workprocess.download_path key not found on Parameters file."
        logger(log, "e", msm)
        return False    # Can be changed to return False

    # filter workprocess in queue to ingestion
    qs_workprocess = WorkProcessNhanes.objects.filter(
        status='pending',
        is_download=True
    )
    if not qs_workprocess.exists():
        msm = "No WorkProcess in queue to ingestion."
        logger(log, "i", msm)
        return False

    # Process NHANES ingestion by Cycle and Dataset
    for qry_workprocess in qs_workprocess:

        v_time_start_dataset = time.time()

        msm = f"Starting ingestion for {qry_workprocess.cycle.cycle} - {qry_workprocess.dataset.dataset}." # noqa E501
        logger(log, "i", msm)

        # set file names
        dataset = qry_workprocess.dataset.dataset
        if qry_workprocess.cycle.year_code == '':
            name_file = f"{dataset}"
        elif qry_workprocess.cycle.year_code is not None:
            name_file = f"{dataset}_{qry_workprocess.cycle.year_code}"
        else:
            name_file = f"{dataset}"

        if qry_workprocess.datasetcycle.has_special_year_code:
            if qry_workprocess.datasetcycle.special_year_code is not None:
                name_file = f"{dataset}_{qry_workprocess.datasetcycle.special_year_code}"  # noqa E501
            else:
                name_file = f"{dataset}"

        # setting folder to hosting download files
        base_dir = download_path / "downloads"  # str(qry_workprocess.cycle.base_dir)
        os.makedirs(base_dir, exist_ok=True)

        data_file = base_dir / f"{name_file}.XPT"
        doc_file = base_dir / f"{name_file}.htm"

        # set URLs
        data_url = qry_workprocess.cycle.get_dataset_url(f"{name_file}.XPT")
        doc_url = data_url.replace('XPT', 'htm')

        # start download files
        file_types = {
            'XPT': 'XPT',
            'htm': 'htm'
        }
        for file_type, extension in file_types.items():
            # set file type and url
            if file_type == 'XPT':
                file_name = data_file
                url = data_url
            else:
                file_name = doc_file
                url = doc_url
            sleep(np.random.rand())  # avoit 429 error / too many requests
            if not os.path.exists(file_name):
                status, error = ingestion_utils.download_nhanes_file(
                    log,
                    url,
                    file_name
                    )
                if status:
                    msm = f"The {name_file}.{extension} file was downloaded."
                    logger(log, "s", msm)
                else:
                    break
            else:
                status = True
                msm = f"File {file_name}.{extension} already exists. Skipping download."
                logger(log, "i", msm)

        if not status:
            qry_workprocess.status = error
            qry_workprocess.save()
            msm = f"No file to {name_file}.{extension}"
            logger(log, "i", msm)
            continue

        # get data from XPT file
        try:
            df, meta_df = ingestion_utils.get_data_from_xpt(log, data_file)
        except Exception as e:
            try:
                os.remove(data_file)
                os.remove(doc_file)
            except OSError as f:
                msm = f"Error deleting file: {f}"
                logger(log, "e", msm)
            msm = f"Error reading XPT file: {e}"
            logger(log, "e", msm)
            qry_workprocess.status = 'error'
            qry_workprocess.save()
            continue

        # get data from HTM file
        variable_df, code_table = ingestion_utils.get_data_from_htm(dataset, doc_file, meta_df)
        if variable_df is None or code_table is None:
            msm = f"Error reading htm file: {doc_file}"
            logger(log, "e", msm)
            qry_workprocess.status = 'error'
            qry_workprocess.save()
            continue

        # Normalization of the variable names
        df_metadata = pd.merge(
            variable_df,
            meta_df[['Variable', 'Type']],
            left_on='VariableName',
            right_on='Variable',
            how='left'
        )

        # Converter code_table to JSON
        json_tables = {
            key: value.to_json(orient='records') for key, value in code_table.items()
        }

        # Create a column in 'combined_df' for the code table
        df_metadata['CodeTables'] = df_metadata['VariableName'].map(json_tables)

        if load_type in ['csv', 'both']:
            # Save the metadata in CSV or DB
            csv_file_path = str(data_file).replace('.XPT', '_data.csv')
            df.to_csv(csv_file_path)
            doc_file_path = str(doc_file).replace('.htm', '_meta.csv')
            df_metadata.to_csv(doc_file_path)
            msm = f"Saved files: {csv_file_path} and {doc_file_path}"
            logger(log, "s", msm)

        elif load_type in ['db', 'both']:
            # Salve the NHANES metadata in the database
            check_return = ingestion_utils.process_and_save_metadata(
                log,
                df_metadata,
                dataset_id=qry_workprocess.dataset.id,
                cycle_id=qry_workprocess.cycle.id,
                load_metadata=load_metadata,
                dataset_cycle_url=url,
                dataset_cycle_description=""  # TODO: Extract JSON from HTML (_parse_nhanes_html_docfile) # noqa E501
                )
            if not check_return:
                msm = f"Error on save metadata in database to {qry_workprocess.cycle.cycle} - {qry_workprocess.dataset.dataset}." # noqa E501
                logger(log, "e", msm)
                qry_workprocess.status = 'error'
                qry_workprocess.save()
                continue

            save_data = config['workprocess']['save_data']
            if save_data is None:
                save_data = True

            # Salve the NHANES data in the database
            check_return = ingestion_utils.save_nhanes_data(
                log,
                df,
                cycle_id=qry_workprocess.cycle.id,
                dataset_id=qry_workprocess.dataset.id,
                save_data=save_data
                )
            if not check_return:
                msm = f"Error on save data in database to {qry_workprocess.cycle.cycle} - {qry_workprocess.dataset.dataset}." # noqa E501
                logger(log, "e", msm)
                qry_workprocess.status = 'error'
                qry_workprocess.save()
                continue

            # Update the WorkProcess table
            time_dataset = int(time.time() - v_time_start_dataset)
            qry_workprocess.source_file_version = "v.0"  # FIX: version
            qry_workprocess.source_file_size = os.path.getsize(data_file)
            qry_workprocess.time = time_dataset
            qry_workprocess.status = 'complete'
            qry_workprocess.records = df.shape[0]
            qry_workprocess.n_samples = df.shape[0]
            qry_workprocess.save()

        # Clean up downloaded files
        try:
            os.remove(data_file)
            os.remove(doc_file)
        except OSError as e:
            msm = f"Error deleting file: {e}"
            logger(log, "e", msm)

        msm = f"Finished ingestion for {qry_workprocess.cycle.cycle} - {qry_workprocess.dataset.dataset} in {time_dataset} seconds." # noqa E501
        logger(log, "s", msm)

    total_time = int(time.time() - v_time_start_process)
    logger(
        log,
        "s",
        f"The Master Data was imported in {total_time} seconds."
    )
    return True
