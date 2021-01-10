from pydicom.filewriter import write_file_meta_info

from pynetdicom import AE, evt, AllStoragePresentationContexts
import os

# Implement a handler for evt.EVT_C_STORE
def handle_store(event):
    """Handle a C-STORE request event."""
    PatientID=event.dataset.PatientID
    StudyID = event.dataset.StudyInstanceUID
    #check and create directories
    # Structure: PATIENT -> Study
    if not os.path.exists('DICOMDIR/'+PatientID):
        os.makedirs('DICOMDIR/'+PatientID)
    if not os.path.exists('DICOMDIR/'+PatientID+'/'+StudyID):
        os.makedirs('DICOMDIR/'+PatientID+'/'+StudyID)
    #TODO check for errors, disk size avaliable
    with open('DICOMDIR/'+PatientID+'/'+StudyID+'/'+event.request.AffectedSOPInstanceUID, 'wb') as f:
        #TODO lookup for compression
        # Write the preamble and prefix
        f.write(b'\x00' * 128)
        f.write(b'DICM')
        # Encode and write the File Meta Information
        write_file_meta_info(f, event.file_meta)
        # Write the encoded dataset
        f.write(event.request.DataSet.getvalue())
        #Write success? --- 
        #TODO Sadd to DB : Patients,Studies,Series,Images


    # Return a 'Success' status
    return 0x0000

handlers = [(evt.EVT_C_STORE, handle_store)]

# Initialise the Application Entity
ae = AE()
# Unlimited PDU size
ae.maximum_pdu_size = 0

# Add the supported presentation contexts
ae.supported_contexts = AllStoragePresentationContexts

# Start listening for incoming association requests
ae.start_server(('', 11112), evt_handlers=handlers)