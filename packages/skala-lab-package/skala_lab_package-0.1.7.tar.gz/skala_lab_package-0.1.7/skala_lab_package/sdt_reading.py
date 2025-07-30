import sdtfile
import numpy as np
import zipfile  
    
def read_sdt_info_brukerSDT(filename):  
    """ 
    modified from CGohlke sdtfile.py to read bruker 150 card data
    gives tarr, x.shape,y.shape,t.shape,c.shape
    """
    ## HEADER
    measure_info = []
    dtype = np.dtype(sdtfile.sdtfile.MEASURE_INFO)
    with open(filename, 'rb') as fh:
        ## HEADER
        header = np.rec.fromfile(fh, dtype=sdtfile.sdtfile.FILE_HEADER, shape=1, byteorder='<')
        fh.seek(header.meas_desc_block_offs[0])
        for _ in range(header.no_of_meas_desc_blocks[0]):
            measure_info.append(
                np.rec.fromfile(fh, dtype=dtype, shape=1, byteorder='<'))
            fh.seek(header.meas_desc_block_length[0] - dtype.itemsize, 1)
    
    times = []
    block_headers = []

    try:
        routing_channels_x = measure_info[0]['image_rx'][0]
    except:
        routing_channels_x = 1

    offset = header.data_block_offs[0]
 
    with open(filename, 'rb') as fh:
        for _ in range(header.no_of_data_blocks[0]): ## 
            fh.seek(offset)
            # read data block header
            bh = np.rec.fromfile(fh, dtype=sdtfile.sdtfile.BLOCK_HEADER, shape=1,
                                 byteorder='<')[0]
            block_headers.append(bh)
            # read data block
            mi = measure_info[bh.meas_desc_block_no]
            
            dtype = sdtfile.sdtfile.BlockType(bh.block_type).dtype
            dsize = bh.block_length // dtype.itemsize
            
            t = np.arange(mi.adc_re[0], dtype=np.float64)
            t *= mi.tac_r / float(mi.tac_g * mi.adc_re)
            times.append(t)
            offset = bh.next_block_offs
        return (header.data_block_offs[0], times, [mi.scan_x[0], mi.scan_y[0], mi.adc_re[0], routing_channels_x])
    
    
def read_sdt150(filename):
    """
    filenamme: str
    output: dataSDT: np.ndarray
    read sdt file and return data in CXYT format
    """
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    offset, t, XYTC = read_sdt_info_brukerSDT(filename)
    try: 
        # if the input file is sdt_zipped
        with zipfile.ZipFile(filename) as myzip:
            z1 = myzip.infolist()[0]  # "data_block"
            with myzip.open(z1.filename) as myfile:
                dataspl = myfile.read()
    except:
        # if the input file is unzipped 
        with open(filename, 'rb') as myfile:
            myfile.seek(offset)
            dataspl = myfile.read()
            
    dataSDT = np.fromstring(dataspl, np.uint16)
    
    if XYTC[3] == 1:
        # reduce the 4D data to 3d (CXYT to XYT)
        dataSDT = dataSDT[:XYTC[0] * XYTC[1] * XYTC[2]].reshape([XYTC[0], XYTC[1], XYTC[2]])
    # reshape XYTC to CXYT
    elif XYTC[3] > 1:
        # Check for empty channels and filter them out
        non_empty_channels =  len(dataSDT) // (XYTC[0] * XYTC[1] * XYTC[2])
        if non_empty_channels == 1:
            # If only one channel is present, reshape to 3D
            dataSDT = dataSDT[:XYTC[0] * XYTC[1] * XYTC[2]].reshape([XYTC[0], XYTC[1], XYTC[2]])
        else:
            dataSDT = dataSDT[:XYTC[0] * XYTC[1] * XYTC[2] * XYTC[3]].reshape([XYTC[3], XYTC[0], XYTC[1], XYTC[2]])

   
    return dataSDT