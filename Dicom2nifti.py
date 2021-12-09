'''
Data Directory:
Subject 01 : | CT - | CT dicoms 
             | MR - | T1 dicoms
                    | T2 dicoms
Subject 02: ...

'''
import os
import SimpleITK as sitk


base_dir = <path_to_data>
spacing = (0.7, 0.7, 0.7)

def dcm2nifti(path, mod, scan_id):
    """Converts individual dicoms to a 3D nifti scan"""
    file_path = os.path.join(path, mod, scan_id)
    series_IDs = sitk.ImageSeriesReader.GetGDCMSeriesIDs(file_path)
    nb_series = len(series_IDs)
    series_file_names = sitk.ImageSeriesReader.GetGDCMSeriesFileNames(file_path, series_IDs[0])
    series_reader = sitk.ImageSeriesReader()

    series_reader.SetFileNames(series_file_names)
    image3D = series_reader.Execute()
    print(image3D.GetSize())
    return image3D

def resample3d(x, original_spacing, new_spacing, resampling_mode):
    """Resamples the given array into new spacing"""
    original_size = x.GetSize()
    I_size = [int(spacing / new_s * size)
              for spacing, size, new_s in zip(original_spacing, original_size, new_spacing)]

    I = sitk.Image(I_size, x.GetPixelIDValue())
    I.SetSpacing(new_spacing)
    I.SetOrigin(x.GetOrigin())
    I.SetDirection(x.GetDirection())

    resample = sitk.ResampleImageFilter()
    resample.SetReferenceImage(I)
    resample.SetInterpolator(resampling_mode)
    resample.SetTransform(sitk.Transform())
    I = resample.Execute(x)
    return I


'''To convert dicoms of multiple sequences into nifti files'''
for i in os.listdir(base_dir):
    dir_path = os.path.join(base_dir, i)
    if not dir_path.startswith('.') and os.path.isdir(dir_path):
        print(dir_path)
        subj_id = f'_S{i}'
        for item in os.listdir(dir_path):
            if not item.startswith('.'):
                print(item)
                for scan_mod in os.listdir(os.path.join(dir_path, item)):
                    print(scan_mod)
                    if not scan_mod.startswith('.'):

                        try:
                            os.makedirs(os.path.join(dir_path, 'nifti_files'))
                        except OSError:
                            pass

                        image3D = dcm2nifti(dir_path, item, scan_id=scan_mod)
                        print('saving scan: ', scan_mod, subj_id, '.nii.gz')
                        sitk.WriteImage(image3D, (dir_path + '/nifti_files/' + scan_mod + subj_id + '.nii.gz'))

        # RESAMPLE
        try:
            os.makedirs(os.path.join(dir_path, 'Processed'))
        except OSError:
            pass

        for k in os.listdir(dir_path + '\\nifti_files'):
            if k.endswith('.nii.gz'):
                print('Saving Resampled scans: ', k[:k.find('.nii.gz')])
                img1 = sitk.DICOMOrient(sitk.ReadImage(os.path.join(dir_path, 'nifti_files',
                                                                    k)))  # Loads image and orients it in default: RAI
                newspacing = spacing
                if 'mask' in k:
                    resampling_mode = sitk.sitkNearestNeighbor
                else:
                    resampling_mode = sitk.sitkBSpline

                resamp_img2 = resample3d(img1, img1.GetSpacing(), newspacing, resampling_mode)
                sitk.WriteImage(resamp_img2, os.path.join(dir_path, 'Processed') + '/' + k[:k.find(
                    '.nii.gz')] + '_resampled.nii.gz')
