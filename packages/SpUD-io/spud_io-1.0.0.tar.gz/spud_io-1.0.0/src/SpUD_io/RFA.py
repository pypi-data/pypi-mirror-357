# RFA.py
# This file is a module that allows a user to more easily manipulate output data from SXXI. This module contains a class declaration
#     for an RFA object, useful methods for manipulating RFA objects, a function to import records in either GMF or SFAF format,
#     functions for exporting the data in particular formats, and functions for converting SXXI values into more readable formats.
# The current version of this module should be considered an 'alpha' version as it contains minimal documentation and error handling.

import os
import datetime
import re
from datetime import date
import sys

# An RFA object that represents a Radio Frequency Assignment from SXXI using fields derived from both GMF and SFAF format
# Some SXXI columns can be repeated to represent multiple values for a particular column which are represented as lists
#     in this object declaration. Columns that can only ever have one value are represented as strings.
class RFA:
    def __init__(self):
        self.serial_number = None
        self.agency_action_number = None
        self.classification = None
        self.bureau = None
        self.agency = None
        self.record_type = None
        self.main_function_id = None
        self.intermediate_function_id = None
        self.detailed_function_id = None
        self.irac_docket_number = []
        self.docket_number_old = None
        self.sxxi_frequency = None
        self.sxxi_frequency_upper_limit = None
        self.sxxi_excluded_frequency_bands = []
        self.sxxi_paired_frequency = []
        self.gmf_time = None
        self.irac_notes = []
        self.free_text = []
        self.misc_agency_data = []
        self.fas_agenda = []
        self.supplementary_details = ''
        self.point_of_contact = None
        self.poc_name = None
        self.poc_phone_number = None
        self.poc_verification_date = None
        self.joint_agency_names = []
        self.international_coordination_id = None
        self.canadian_coordination_comments = []
        self.mexican_coordination_comments = []
        self.user_net_code = []
        # Emission group
        self.station_class = []
        self.emission_designator = []
        self.sxxi_power = []
        # These two are not used in DoC records
        self.effective_radiated_power = []
        self.power_augmentation = []
        # Transmitter group
        self.tx_state_country_code = None
        self.tx_antenna_location = None
        self.tx_station_control = None
        self.tx_station_call_sign = None
        self.tx_antenna_latitude = None
        self.tx_antenna_longitude = None
        self.tx_authorized_radius = None
        self.tx_inclination_angle = None
        self.tx_apogee = None
        self.tx_perigee = None
        self.tx_period_of_orbit = None
        self.tx_number_of_satellites = None
        self.tx_power_density = None
        self.tx_equipment_nomenclature = []
        self.tx_system_name = None
        self.tx_number_of_stations = None
        self.tx_ots_equipment = None
        self.tx_radar_tunability = None
        self.tx_pulse_duration = []
        self.tx_pulse_repetition_rate = []
        self.tx_antenna_name = None
        self.tx_antenna_nomenclature = None
        self.tx_antenna_gain = []
        self.tx_antenna_elevation = None
        self.tx_antenna_feed_point_height = None
        self.tx_antenna_horizontal_beamwidth = None
        self.tx_antenna_azimuth = None
        self.tx_antenna_orientation = None
        self.tx_antenna_polarization = None
        self.tx_jsc_area_code = None
        # Receiver group
        self.rx_state_country_code = []
        self.rx_antenna_location = []
        self.rx_control_id_and_server_system_id = []
        self.rx_antenna_latitude = []
        self.rx_antenna_longitude = []
        self.rx_station_call_sign = []
        self.rx_authorized_radius = []
        self.rx_repeater_indicator = []
        self.rx_inclination_angle = []
        self.rx_apogee = []
        self.rx_perigee = []
        self.rx_period_of_orbit = []
        self.rx_number_of_satellites = []
        self.rx_equipment_nomenclature = []
        self.rx_antenna_name = []
        self.rx_antenna_nomenclature = []
        self.rx_antenna_gain = []
        self.rx_antenna_elevation = []
        self.rx_antenna_feed_point_height = []
        self.rx_antenna_horizontal_beamwidth = []
        self.rx_antenna_azimuth = []
        self.rx_antenna_orientation = []
        self.rx_antenna_polarization = []
        self.rx_jsc_area_code = []
        # Area authorization
        self.authorized_area_both = []
        self.rx_authorized_area = []
        self.tx_authorized_area = []
        self.excepted_states_both = []
        self.rx_excepted_states = []
        self.tx_excepted_states = []
        self.authorized_states_both = []
        self.rx_authorized_states = []
        self.tx_authorized_states = []
        # Dates
        self.last_transaction_date = None
        self.revision_date = None
        self.authorization_date = None
        self.expiration_date = None
        self.review_date = None
        self.entry_date = None
        self.receipt_date = None
        # Likely not entered into database for now
        # self.foi_exempt = None
        # self.approval_authority = None
        # self.data_source = None
        # self.routine_agenda_item = None
        # custom columns
        self.power_w = []
        self.center_frequency = None
        self.max_power = None
        self.frequency_band = None
        self.bandwidth = None
        self.tx_lat_long = None
        self.rx_lat_long = []

    # This method overrides the default str() function to print the RFA's serial number.
    def __str__(self):
        return f'<RFA: {self.serial_number}>'
    
    def __getitem__(self, item):
        return getattr(self, item)

    # This method is used to convert an RFA object into a string in .csv format.
    # Any fields that contain commas will have all commas converted into semicolons to be compatible with .csv format.
    # Any list-type fields will be joined into a single field seperated by '|' characters.
    # Any date-type fields will be output in mm/dd/yyyy format
    def toCSVRow(self):
        row = []
        for value in self.__dict__.values():
            if isinstance(value, list):
                value = '|'.join(map(str, value))
            elif isinstance(value, date):
                value = value.strftime('%m/%d/%Y')
            elif value is None:
                value = ''
            row.append(value.replace(',',';'))
        return ','.join(row)
    
    # def toCSVRow_formatted(self):
    #     row = []
    #     for key, value in self.__dict__.items():
    #         if key in ['frequency', 'frequency_upper_limit', 'excluded_frequency_bands', 'paired_frequency']:
    #             if isinstance(value, list):
    #                 value = '|'.join(map(formatFrequency, value))
    #             else:
    #                 value = formatFrequency(value)
    #         elif key == 'power':
    #             value = '|'.join(map(formatPower, value))
    #         elif isinstance(value, list):
    #             value = '|'.join(value)
    #         elif isinstance(value, date):
    #             value = value.strftime('%m/%d/%Y')
    #         elif value is None:
    #             value = ''
    #         row.append(value.replace(',',';'))
    #     return ','.join(row)

    # This method is the same as toCSVRow(), but it only outputs specified fields.
    def toCSVRow_NWSFormat(self):
        main_function_id = self.main_function_id.replace(',', ';')
        intermediate_function_id = self.intermediate_function_id.replace(',', ';')
        detailed_function_id = self.detailed_function_id.replace(',', ';')
        point_of_contact = self.point_of_contact.replace(',', ';')
        revision_date = self.revision_date.strftime('%m/%d/%Y')
        station_classes = '|'.join(self.station_class)
        emission_designators = '|'.join(self.emission_designator)
        powers = '|'.join(self.sxxi_power)
        tx_antenna_name = '|'.join(self.tx_antenna_name)
        tx_antenna_polarization = '|'.join(self.tx_antenna_polarization)
        tx_antenna_orientation = '|'.join(self.tx_antenna_orientation)
        return f'{self.serial_number},{self.agency_action_number},{main_function_id},{intermediate_function_id},{detailed_function_id},{self.sxxi_frequency},{point_of_contact},{revision_date},{self.tx_state_country_code},{self.tx_antenna_location},{self.tx_antenna_latitude},{self.tx_antenna_longitude},{station_classes},{emission_designators},{powers},{self.last_transaction_date},{self.record_type},{tx_antenna_name},{tx_antenna_polarization},{tx_antenna_orientation},{self.tx_station_call_sign}'
    
    def toCSVRow_TrackerFormat(self):
        point_of_contact = self.point_of_contact.replace(',', ';')
        return f'{self.serial_number},{self.agency_action_number},{self.revision_date},{point_of_contact}'


# This function expects a .txt file which was generated by SXXI using any of the SFAF 1 Column or GMF 1 Column output options
#     and returns a list of RFA objects that correspond one-to-one with records found in the file. This function converts
#     records from either format into a joined format. It should be noted that there are some columns in SFAF format that are
#     not present in GMF format, so the resulting list of RFAs may have slightly different values depending on if an SFAF
#     1 Column or GMF 1 Column file was used.
# All column tags from GMF and SFAF format should be included, but this module was developed from an unclassifed release of SXXI
#     with unclassified data, so classified fields will not be handled. Any unrecognized tags will be printed to the console
#     along with the serial number of the record in which they were found.
# NOTE: If using an SFAF 1 Column output that only contains a subset of columns and not the full record, the '005' column which
#     contains the record classification is required to detect the beginning of an new record. This will be fixed in later versions.
def importRFAsFrom1ColFile(filename):
    with open(filename, 'r') as iFile:
        lines = iFile.readlines()
    mode = 'assignment'
    if '_p_' in filename:
        mode = 'proposal'
    return importRFAs(lines, mode)

def importRFAs(lines, mode='assignment'):
    # regular expression strings
    receiver_group_tag = '(.*),R\d{2}$'

    serial_suffix = ''
    if mode == 'proposal':
        serial_suffix = 'p'

    RFAs = []
    rfa = None
    for line_no, line in enumerate(lines, start=1):
        if line == '':
            continue
        # This is some error handling in the rare case that a record has a row with a tag but no value.
        try:
            tag, value = line.strip().split(maxsplit=1)
        except ValueError as err:
            # print(f'{type(err)}: {err}')
            tag = line.strip()
            value = ''
            if tag != '115.':
                if rfa is not None and rfa.serial_number is not None:
                    raise Exception(f'RFA with serial number {rfa.serial_number} has no value for tag {tag}') from None
                else:
                    raise Exception(f'Line number {line_no} has no value for tag {tag}') from None
            else:
                continue
        except Exception as err:
            if rfa is not None and rfa.serial_number is not None:
                print(f'Unexpected Error: {type(err)} on RFA with serial number {rfa.serial_number}', file=sys.stderr)
            else:
                print(f'Unexpected Error: {type(err)} on line number {line_no}', file=sys.stderr)
            raise err
        # Remove the ',R##' tags from values in receiver groups past the first. This only applies to files in SFAF format.
        if matches := re.findall('(.*),R\d{2}$', value):
            # print(f'{value} becomes {matches[0]}')
            value = matches[0]

        # If a value is '$', the loop will skip to the next iteration and not record the value. May need to be handled different at client request.
        if value == '$':
            continue
        try:
            # In these formats, there is no delimination between different records, so the end of a record is determined by the start
            #     of a new one. In GMF format, the first tag of a record is 'SER' which is the serial number, but in SFAF format, the
            #     first tag is '005' which is the security classification.
            if tag == 'SER01' or tag == '005.': #SFAF uses 005 for FOI and CDD in addition to CLA. May need to be handled differently
                if rfa != None:
                    addCustomColumns(rfa)
                    RFAs.append(rfa)
                rfa = RFA()
                if tag == 'SER01':
                    rfa.serial_number = value + serial_suffix
                else:
                    rfa.classification = value
            elif tag == '102.':
                # print(value)
                rfa.serial_number = value + serial_suffix
            elif tag == 'TYP01' or tag == '010.':
                rfa.record_type = value
            elif tag == 'DAT01' or tag == '911.':
                rfa.last_transaction_date = formatGMFDate(value) if tag == 'DAT01' else formatSFAFDate(value)
            elif tag == 'CLA01': 
                rfa.classification = value
            elif tag == 'FOI01':
                # rfa.foi_exempt = value
                continue
            elif tag == 'ACN01' or tag == '956.':
                rfa.agency_action_number = value
            elif tag == 'EXD01' or tag == '141.':
                rfa.expiration_date = formatGMFDate(value) if tag == 'EXD01' else formatSFAFDate(value)
            elif tag == '142.':
                rfa.review_date = formatSFAFDate(value)
            elif tag == '144.':
                # rfa.approval_authority = value
                continue
            elif tag == 'BUR01' or tag == '203.':
                rfa.bureau = value
            elif tag == '200.':
                rfa.agency = value
            elif tag[:3] == 'NET' or tag[:3] == '208':
                rfa.user_net_code.append(value)
            elif tag == 'FRQ01':
                rfa.sxxi_frequency = value
            elif tag == '110.':
                if '-' in value:
                    unit = value[0]
                    lower, upper = value[1:].split('-')
                    rfa.sxxi_frequency = unit + lower
                    rfa.sxxi_frequency_upper_limit = unit + upper
                else:
                    rfa.sxxi_frequency = value
            elif tag[:3] == 'PRD' or tag[:3] == '506':
                rfa.sxxi_paired_frequency.append(value)
            elif tag == 'FRU01':
                rfa.sxxi_frequency_upper_limit = value
            elif tag[:3] == 'FBE' or tag[:3] == '111':
                rfa.sxxi_excluded_frequency_bands.append(value)
            elif tag[:3] == 'STC' or tag[:3] == '113':
                rfa.station_class.append(value)
            elif tag[:3] == 'EMS' or tag[:3] == '114':
                rfa.emission_designator.append(value)
            elif tag[:3] == 'PWR' or tag[:3] == '115':
                rfa.sxxi_power.append(value)
            elif tag[:3] == '117':
                rfa.effective_radiated_power.append(value)
            elif tag[:3] == '118':
                rfa.power_augmentation.append(value)
            elif tag == 'TME01' or tag == '130.':
                rfa.gmf_time = value
            elif tag == 'XSC01' or tag == '300.':
                rfa.tx_state_country_code = value
            elif tag == 'XAL01' or tag == '301.':
                rfa.tx_antenna_location = value
            elif tag == 'XLA01':
                rfa.tx_antenna_latitude = value
            elif tag == 'XLG01':
                rfa.tx_antenna_longitude = value
            elif tag == 'XRD01' or tag == '306.':
                rfa.tx_authorized_radius = value
            elif tag[:3] == 'ARB':
                rfa.authorized_area_both.append(value)
            elif tag == 'XAR01':
                rfa.tx_authorized_area.append(value)
            elif tag[:3] == '530':
                if value[:3] == 'ART':
                    rfa.tx_authorized_area.append(value[4:])
                elif value[:3] == 'ARR':
                    rfa.rx_authorized_area.append(value[4:])
                elif value[:3] == 'ARB':
                    rfa.authorized_area_both.append(value[4:])
                else:
                    print(f'Unknown tag in SFAF 530 of record{rfa.serial_number}')
            elif tag[:3] == 'EQS' or tag[:3] == '344':
                rfa.tx_ots_equipment = value
            elif tag == '303.':
                rfa.tx_antenna_latitude = value[:7] #double check if char count is sufficient condition
                rfa.tx_antenna_longitude = value[7:]
            elif tag[:3] == 'XSE' or tag[:3] == '358':
                rfa.tx_antenna_elevation = value
            elif tag[:3] == 'XAH' or tag[:3] == '359':
                rfa.tx_antenna_feed_point_height = value
            elif tag == 'XRC01' or tag == '302.':
                rfa.tx_station_control = value
            elif tag == 'XCL01' or tag == '304.':
                rfa.tx_station_call_sign = value
            elif tag[:3] == 'XAG' or tag[:3] == '357':
                rfa.tx_antenna_gain.append(value)
            elif tag[:3] == 'XAT' or tag[:3] == '354':
                rfa.tx_antenna_name = value
            elif tag[:3] == 'XAK' or tag[:3] == '355':
                rfa.tx_antenna_nomenclature = value
            elif tag[:3] == 'XAZ':
                rfa.tx_antenna_orientation = value
            elif tag[:3] == '362': #Will need additional processing of tag 362
                if ',' in value:
                    rfa.tx_antenna_orientation, rfa.tx_antenna_azimuth = value.split(',')
                else:
                    rfa.tx_antenna_orientation = value
            elif tag[:3] == 'XAA':
                rfa.tx_antenna_azimuth = value
            elif tag[:3] == 'XAP' or tag[:3] == '363':
                rfa.tx_antenna_polarization = value
            elif tag == 'TUN01' or tag == '345.':
                rfa.tx_radar_tunability = value
            elif tag[:3] == 'PDD' or tag[:3] == '346':
                rfa.tx_pulse_duration.append(value)
            elif tag[:3] == 'PRR' or tag[:3] == '347':
                rfa.tx_pulse_repetition_rate.append(value)
            elif tag[:3] == 'XEQ' or tag[:3] == '340':
                rfa.tx_equipment_nomenclature.append(value)
            elif tag[:3] == 'NTT':
                rfa.tx_number_of_stations = value
            elif tag[:3] == 'NAM':
                rfa.tx_system_name = value
            elif tag[:3] == '341':
                rfa.tx_number_of_stations, rfa.tx_system_name = value.split(',')
                if rfa.tx_number_of_stations[0] == 'X':
                    rfa.tx_number_of_stations = None
            elif tag[:3] == '373':
                rfa.tx_jsc_area_code == value
            elif tag[:3] == 'RSC' or tag[:3] == '400':
                rfa.rx_state_country_code.append(value)
            elif tag[:3] == 'RAL' or tag[:3] == '401':
                rfa.rx_antenna_location.append(value)
            elif tag[:3] == 'RLA':
                rfa.rx_antenna_latitude.append(value)
            elif tag[:3] == 'RLG':
                rfa.rx_antenna_longitude.append(value)
            elif tag[:3] == '403':
                rfa.rx_antenna_latitude.append(value[:7])
                rfa.rx_antenna_longitude.append(value[7:])
            elif tag[:3] == 'RSE' or tag[:3] == '458':
                rfa.rx_antenna_elevation.append(value)
            elif tag[:3] == 'RRD' or tag[:3] == '406':
                rfa.rx_authorized_radius.append(value)
            elif tag[:3] == 'RRC' or tag[:3] == '402':
                rfa.rx_control_id_and_server_system_id.append(value)
            elif tag[:3] == 'RCL' or tag[:3] == '404':
                rfa.rx_station_call_sign.append(value)
            elif tag[:3] == 'RAG' or tag[:3] == '457':
                rfa.rx_antenna_gain.append(value)
            elif tag[:3] == 'RAT' or tag[:3] == '454':
                rfa.rx_antenna_name.append(value)
            elif tag[:3] == 'RAK' or tag[:3] == '455':
                rfa.rx_antenna_nomenclature.append(value)
            elif tag[:3] == 'RAH' or tag[:3] == '459':
                rfa.rx_antenna_feed_point_height.append(value)
            elif tag[:3] == 'RAZ' or tag[:3] == '462':
                rfa.rx_antenna_orientation.append(value)
            elif tag[:3] == 'RAA':
                rfa.rx_antenna_azimuth.append(value)
            elif tag[:3] == 'RAZ':
                rfa.rx_antenna_orientation.append(value)
            elif tag[:3] == '462':
                if value.find(',') == -1:
                    rfa.rx_antenna_orientation.append(value)
                else:
                    rfa.rx_antenna_orientation.append(value[:value.find(',')])
            elif tag[:3] == 'RAP' or tag[:3] == '463':
                rfa.rx_antenna_polarization.append(value)
            elif tag[:3] == 'RPT' or tag[:3] == '408':
                rfa.rx_repeater_indicator.append(value)
            elif tag[:3] == 'REQ' or tag[:3] == '440':
                rfa.rx_equipment_nomenclature.append(value)
            elif tag[:3] == '473':
                rfa.rx_jsc_area_code.append(value[0])
            elif tag == 'SPD01' or tag == '321.':
                rfa.tx_power_density = value
            elif tag[:3] == 'XBW' or tag[:3] == '360':
                rfa.tx_antenna_horizontal_beamwidth =value
            elif tag == 'XIN01' or tag == '315.':
                rfa.tx_inclination_angle = value
            elif tag == 'XAE01' or tag == '316.':
                rfa.tx_apogee = value
            elif tag == 'XPE01' or tag == '317.':
                rfa.tx_perigee = value
            elif tag == 'XPD01' or tag == '318.':
                rfa.tx_period_of_orbit = value
            elif tag == 'XNR01' or tag == '319.':
                rfa.tx_number_of_satellites = value
            elif tag[:3] == 'RBW' or tag[:3] == '460':
                rfa.rx_antenna_horizontal_beamwidth.append(value)
            elif tag[:3] == 'RIN' or tag[:3] == '415':
                rfa.rx_inclination_angle.append(value)
            elif tag[:3] == 'RAE' or tag[:3] == '416':
                rfa.rx_apogee.append(value)
            elif tag[:3] == 'RPE' or tag[:3] == '417':
                rfa.rx_perigee.append(value)
            elif tag[:3] == 'RPD' or tag[:3] == '418':
                rfa.rx_period_of_orbit.append(value)
            elif tag[:3] == 'RNR' or tag[:3] == '419':
                rfa.rx_number_of_satellites.append(value)
            elif tag[:3] == 'JNT' or tag[:3] == '147':
                rfa.joint_agency_names.append(value)
            elif tag == 'MFI01' or tag == '511.':
                rfa.main_function_id = value
            elif tag == 'IFI01' or tag == '512.':
                rfa.intermediate_function_id = value
            elif tag[:3] == 'DFI' or tag[:3] == '513':
                rfa.detailed_function_id = value
            elif tag[:3] == 'NTS' or tag[:3] == '500':
                rfa.irac_notes.append(value)
            elif tag[:3] == '117':
                rfa.effective_radiated_power.append(value)
            elif tag == 'ICI01' or tag == '151.':
                rfa.international_coordination_id = value
            elif tag[:3] == 'CAN':
                rfa.canadian_coordination_comments.append(value)
            elif tag[:3] == 'MEX':
                rfa.mexican_coordination_comments.append(value)
            elif tag[:3] == '152':
                if value[0] == 'C':
                    rfa.canadian_coordination_comments.append(value[2:])
                elif value[0] == 'M':
                    rfa.mexican_coordination_comments.append(value[2:])
                else:
                    print(f'Unrecognized format for SFAF 152 in record {rfa.serial_number}')
            elif tag[:3] == 'NOT' or tag[:3] == '501':
                rfa.free_text.append(value)
            elif tag == 'DOC01' or tag == '108.':
                rfa.docket_number_old = value
            elif tag == 'POC01' or tag == '803.':
                rfa.point_of_contact = value
                rfa.poc_name, rfa.poc_phone_number, rfa.poc_verification_date = rfa.point_of_contact.split(',')
                rfa.poc_verification_date = formatGMFDate(rfa.poc_verification_date)
            elif tag[:3] == 'AGN' or tag[:3] == '503':
                rfa.misc_agency_data.append(value)
            elif tag[:3] == 'FAS' or tag[:3] == '504':
                rfa.fas_agenda.append(value)
            elif tag == 'RTN01' or tag == '958.':
                # rfa.routine_agenda_item = value
                continue
            elif tag[:3] == 'SUP' or tag[:3] == '520':
                if rfa.supplementary_details != '':
                    rfa.supplementary_details += f' {value}'
                else:
                    rfa.supplementary_details = value
            elif tag[:3] == 'AUS' or tag[:3] == '103':
                rfa.irac_docket_number.append(value)
            elif tag == 'AUD01' or tag == '107.':
                rfa.authorization_date = formatGMFDate(value) if tag == 'AUD01' else formatSFAFDate(value)
            elif tag == 'RVD01' or tag == '143.':
                rfa.revision_date = formatGMFDate(value) if tag == 'RVD01' else formatSFAFDate(value)
            elif tag[:3] == 'AST' or tag[:3] == '531':
                if value[:3] == 'ESB':
                    rfa.excepted_states_both.append(value[4:])
                elif value[:3] == 'ESR':
                    rfa.rx_excepted_states.append(value[4:])
                elif value[:3] == 'EST':
                    rfa.tx_excepted_states.append(value[4:])
                elif value[:3] == 'LSB':
                    rfa.authorized_states_both.append(value[4:])
                elif value[:3] == 'LSR':
                    rfa.rx_authorized_states.append(value[4:])
                elif value[:3] == 'LST':
                    rfa.tx_authorized_states.append(value[4:])
                else:
                    print(f'Unrecognized format for SFAF 531 or GMF AST in record {rfa.serial_number}')
            elif tag == '924.':
                # rfa.data_source = value
                continue
            elif tag == '927.':
                rfa.entry_date = formatSFAFDate(value)
            elif tag == '928.':
                rfa.receipt_date = formatSFAFDate(value)
            else:
                print(f'Unknown Tag {tag} at line {line_no}')
        except Exception as error:
            if rfa is not None and rfa.serial_number is not None:
                print(f'Unexpected Error: {type(error)} on RFA with serial number {rfa.serial_number}', file=sys.stderr)
            else:
                print(f'Unexpected Error: {type(error)} in line {line_no}', file=sys.stderr)
            raise error
    addCustomColumns(rfa)
    RFAs.append(rfa)
    return RFAs


# This function takes a list of RFAs and a string that represents the name of a .csv file, and converts each RFA
#     into .csv format, and exports them into a new file where each record is on its own line. The first line of
#     the file is a header.
# This function includes file creation and writing which will require additional error handling to ensure proper
#     resource handling and protection. This will be included in future versions.
def exportRFAsToCSV(RFAs, filename='output.csv'):
    if os.path.isdir('./outputs/'):
        filename = './outputs/' + filename
    with open(filename, 'w') as oFile:
        headers = ','.join(RFAs[0].__dict__.keys())
        oFile.write(f'{headers}\n')
        for rfa in RFAs:
            oFile.write(f'{rfa.toCSVRow()}\n')


def exportRFAsToCSV_formatted(RFAs, filename='output.csv'):
    if os.path.isdir('./outputs/'):
        filename = './outputs/' + filename
    with open(filename, 'w') as oFile:
        headers = ','.join(RFAs[0].__dict__.keys())
        oFile.write(f'{headers}\n')
        for rfa in RFAs:
            oFile.write(f'{rfa.toCSVRow_formatted()}\n')


# This function is the same as exportRFAsToCSV(), but uses the NWS format.
def exportRFAsToCSV_NWSFormat(RFAs, filename='output.csv'):
    if os.path.isdir('./outputs/'):
        filename = './outputs/' + filename
    with open(filename, 'w') as oFile:
        oFile.write('Serial Number,Action Number,Main Function Identifier,Intermediate Function Identifier,Detailed Function Identifier,Frequency,Point of Contact,Revision Date,Transmitter State/Country Code,Transmitter Antenna Location,Transmitter Latitude,Transmitter Longitude,Station Class(es),Emission Designator(s),Power(s),Last Transaction Date,Type of Action,Transmitter Antenna Name,Transmitter Antenna Polarization,Transmitter Antenna Orientation,Station Call Sign\n')
        for rfa in RFAs:
            oFile.write(f'{rfa.toCSVRow_NWSFormat()}\n')


def exportRFAsToCSV_TrackerFormat(RFAs, filename='output.csv'):
    if os.path.isdir('./outputs/'):
        filename = './outputs/' + filename
    with open(filename, 'w') as oFile:
        oFile.write('Serial Number,Action Number,Revision Date,Point of Contact\n')
        for rfa in RFAs:
            oFile.write(f'{rfa.toCSVRow_TrackerFormat()}\n')


# This function converts a frequency in SXXI format into kHz. The purpose of this function is to create a sortable
#     format for frequencies.
# Future versions will include formatting options.
def formatFrequency(SXXI_frequency):
    unit = SXXI_frequency[0].lower()
    quantity = SXXI_frequency[1:]

    if unit == 'h':
        conversion = 0
    elif unit == 'k':
        conversion = 3
    elif unit == 'm':
        conversion = 6
    elif unit == 'g':
        conversion = 9
    elif unit == 't':
        conversion = 12
    else:
        print(f'Unknown unit \'{unit}\'in frequency format')

    return str(float(quantity) * (10 ** conversion))


def formatFrequencyBand(SXXI_frequency_band):
    unit = SXXI_frequency_band[0].lower()
    lower_end, upper_end = map(formatFrequency, list(map(lambda x: unit + x, SXXI_frequency_band[1:].split('-'))))
    return (lower_end, upper_end)


# This function converts a date in GMF format into standard dd/mm/yyyy format.
def formatGMFDate(GMF_date):
    year = GMF_date[:2]
    month = GMF_date[2:4]
    day = GMF_date[4:]

    if int(year) > 60:
        year = '19' + year
    else:
        year = '20' + year

    return datetime.date(int(year), int(month), int(day))


# This function converts a date in SFAF format into standard dd/mm/yyyy format.
def formatSFAFDate(SFAF_date):
    year = SFAF_date[:4]
    month = SFAF_date[4:6]
    day = SFAF_date[6:]
    return datetime.date(int(year), int(month), int(day))


# This function converts a power in SXXI format into Watts.
def formatPower(SXXI_power):
    if SXXI_power is None or SXXI_power == '':
        return 0
    unit = SXXI_power[0]
    quantity = SXXI_power[1:]

    if unit == 'W':
        conversion = 0
    elif unit == 'K':
        conversion = 3
    elif unit == 'M':
        conversion = 6

    return float(quantity) * (10 ** conversion)


def formatLatLong(SXXI_latitude, SXXI_longitude):
    lat_degrees, lat_minutes, lat_seconds, lat_sign = [(SXXI_latitude[i:i+2]) for i in range(0, len(SXXI_latitude), 2)]
    long_degrees, long_minutes, long_seconds, long_sign = SXXI_longitude[:3], SXXI_longitude[3:5], SXXI_longitude[5:7], SXXI_longitude[7]

    if lat_sign == 'N':
        lat_sign = 1
    else:
        lat_sign = -1

    if long_sign == 'E':
        long_sign = 1
    else:
        long_sign = -1

    lat_degrees = lat_sign * DMSToDD(lat_degrees, lat_minutes, lat_seconds)
    long_degrees = long_sign * DMSToDD(long_degrees, long_minutes, long_seconds)

    return str(lat_degrees) + ',' + str(long_degrees)


def DMSToDD(degrees, minutes, seconds):
    return float(degrees) + (float(minutes) / 60) + (float(seconds) / 3600)


def decodeEmissionDesignator(emissionDesignator):
    before_point = ''
    after_point = ''
    unit = None
    for char in emissionDesignator:
        if unit is None:
            if char.isnumeric():
                before_point += char
            else:
                unit = char
        else:
            if char.isnumeric():
                after_point += char
            else:
                break
    if unit == 'N':
        return None
    else:
        unit = unit.lower()
        if after_point == '':
            value = float(before_point)
        else:
            value = float(before_point + '.' + after_point)
        if unit == 'h':
            return value
        elif unit == 'k':
            return value * (10 ** 3)
        elif unit == 'm':
            return value * (10 ** 6)
        elif unit == 'g':
            return value * (10 ** 9)


def addCustomColumns(rfa):
    for power in rfa.sxxi_power:
        rfa.power_w.append(formatPower(power))

    max_power = 0
    for power in rfa.power_w:
        power = float(power)
        if power > max_power:
            max_power = power
    rfa.max_power = str(max_power)

    bandwidth = 0
    for emission_designator in rfa.emission_designator:
        band = decodeEmissionDesignator(emission_designator)
        if band is not None and band > bandwidth:
            bandwidth = band
    rfa.bandwidth = str(bandwidth)

    if rfa.sxxi_frequency_upper_limit is not None:
        lower_limit = float(formatFrequency(rfa.sxxi_frequency))
        upper_limit = float(formatFrequency(rfa.sxxi_frequency_upper_limit))
        rfa.frequency_band = '['+str(lower_limit) + ',' + str(upper_limit)+']'
        rfa.center_frequency = str(lower_limit + ((upper_limit - lower_limit) / 2))
    else:
        rfa.center_frequency = formatFrequency(rfa.sxxi_frequency)
        rfa.frequency_band = '['+str(float(rfa.center_frequency) - (bandwidth / 2)) + ',' + str(float(rfa.center_frequency) + (bandwidth / 2))+']'

    
    
    if rfa.tx_antenna_latitude is not None and rfa.tx_antenna_longitude is not None:
        rfa.tx_lat_long = formatLatLong(rfa.tx_antenna_latitude, rfa.tx_antenna_longitude)

    for rx_lat, rx_long in zip(rfa.rx_antenna_latitude, rfa.rx_antenna_longitude):
        # print(rx_lat, rx_long)
        rfa.rx_lat_long.append(formatLatLong(rx_lat, rx_long))