from apstools.callbacks.callback_base import FileWriterCallbackBase
from datetime import datetime
import logging 
import os
import json
import pandas as pd


class CSVCallback(FileWriterCallbackBase):
    """
    Callback class for exporting data to CSV files.

    The CSV files will be exported to file_path.
    If _receivers is not empty, the csv file is sent to the receivers.

    Usage:
    csv_export = CSVCallback()
    RE.subscribe(csv_export)

    Parameters:
        _receivers (list): List of receivers.
        file_path (str): File path for CSV files.
        logger(logging instance): If not None, exceptions are logged here
    """

    def __init__(self, _receivers=[], file_path=None, logger=None):
        """
        Initialize the CSVCallback.
        """
        super().__init__()
        self.receivers = _receivers
        self.file_path = file_path
        self.logger = logger

    def start(self, doc):
        """
        Extend start function from parent class callback_base.py to capture different writing logic.
        Executed when the Start document is created.

        Parameters:
        doc (dict): The Bluesky start document.

        """
        super().start(doc)
        self.start_doc = doc
        for receiver in self.receivers:
            receiver.collectMetaData(doc)

    def event(self, doc):
        """
        Process a single "row" of data.
        Exectuted when an Event document is created.

        Parameters:
        doc (dict): The Bluesky document containing event data.

        """
        if not self.scanning:
            return
        descriptor_uid = doc["descriptor"]
        descriptor = self.acquisitions.get(descriptor_uid)
        if descriptor is not None:
            for k, v in doc["data"].items():
                data = descriptor["data"].get(k)
                if data is None:
                    print(f"entry key {k} not found in descriptor of {descriptor['stream']}")
                else:
                    data["data"].append(v)
                    data["time"].append(doc["time"])  # take the event time rather than the time the individual item returned

    def make_file_name(self):
        """
        Generate a file name to be used.

        This is self.path+%Y_%m_%d)+'.csv'

        Returns:
        str: The generated file name.

        """
        date_string = datetime.now().strftime('%Y_%m_%d')
        fname = f"{self.scan_id:05d}" #_{self.uid[:7]}"
        path = os.path.abspath(self.file_path)
        #path = os.path.join(path, date_string)
        path = os.path.join(path, 'csv')
        os.makedirs(path, exist_ok=True)
        return os.path.join(path, fname)

    def writer(self):
        """
        Write the collected data to CSV files.

        """
        for stream_name, stream_data in sorted(self.streams.items()):
            export_d = {}

            for data_key, data in self.acquisitions[stream_data[0]]['data'].items():
                # Test if the data is just one dimension, if not don't export to csv
                if data['shape'] == [] and not data['external']:
                    export_d[data_key] = data['data']
                    export_d['time'] = data['time']

            export_df = pd.DataFrame(data=export_d)
            if 'time' in export_df:
                export_df = export_df[['time'] + [col for col in export_df.columns if col != 'time']]

            # save the dataframe of this element of the stream (like biologic, baseline, primary) as a csv file
            fname = (self.file_name or self.make_file_name()) + "_" + str(stream_name) + ".csv"
            try:
                export_df.to_csv(fname)

                # Then export each file to the requested remote locations
                for receiver in self.receivers:
                    receiver.sent(fname)

            except Exception as e:
                if self.logger:
                    self.logger.error(f"CSV Export: Error Exporting {fname}: {e} ")
                else:
                    print((f"CSV Export: Error Exporting {fname}: {e} "))


        # Write the metadata to a json file and export that
        json_object = json.dumps(self.start_doc, indent=4)
        fname = (self.file_name or self.make_file_name()) + "_" + str("meta.json")

        try:
            with open(fname, "w") as outfile:
                outfile.write(json_object)
            # Then export each file to the requested remote locations
            for receiver in self.receivers:
                receiver.sent(fname)
        except Exception as e:
            if self.logger:
                self.logger.error(f"CSV Export: Error Exporting {fname}: {e} ")
            else:
                print(f"CSV Export: Error Exporting {fname}: {e} ")

    def clear(self):
        """
        Clear the callback.

        """
        super().clear()
        self.start_doc = {}

    def change_user(self, username):
        path = "/opt/bluesky/data"
        user_path = os.path.join(path, username)
        if not os.path.exists(user_path):
            os.makedirs(user_path)
            print(f"Folder '{user_path}' created successfully.")
        else:
            print(f"Folder '{user_path}' already exists.")
        self.file_path = user_path