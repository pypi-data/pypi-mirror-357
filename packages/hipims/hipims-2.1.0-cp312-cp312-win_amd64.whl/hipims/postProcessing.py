from glob import glob
import os
import rasterio as rio
import numpy as np
import torch

def exportRaster_tiff(DEM_path, outPutPath, archive_pt=False):
    data_result, mask, demMeta = _load_dem(DEM_path)

    result_list = glob(outPutPath + '/*.pt')
    result_list.sort()

    for result_file in result_list:
        # get data
        internal_data = torch.load(result_file, weights_only=True).cpu().numpy()
        data_result[mask] = internal_data
        
        # generate file name
        topAddress = result_file[:result_file.rfind('.')]
        #timeAddress = result_file[result_file.find('[') +
        #                            1:result_file.find(']')]
        #print(timeAddress)
        outPutName = topAddress + '.tif'
        # write file
        with rio.open(outPutName, 'w', **demMeta) as dest:
            dest.write(data_result, 1)
        
        if (archive_pt == False):
            os.remove(result_file)


def _load_dem(dem_path):
    with rio.open(dem_path) as src:
        demMasked = src.read(1, masked=True)
        meta = src.meta   
    # mask = demMasked.mask 
    mask = np.ma.getmaskarray(demMasked)  # Ensure mask is a numpy.ndarray
    mask = torch.from_numpy(mask.astype(np.bool_))  # Convert to PyTorch tensor
    # mask = (dem == src.nodata) | np.isnan(dem)
    mask = ~mask
    return demMasked, mask, meta