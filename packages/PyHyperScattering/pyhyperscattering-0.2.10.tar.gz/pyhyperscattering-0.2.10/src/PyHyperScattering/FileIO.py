import warnings
import xarray as xr
import numpy as np
import pickle
import math
import h5py
import pathlib
import datetime
import six
import PyHyperScattering
import pandas
import json

from collections import defaultdict
from . import _version
phs_version = _version.get_versions()['version']



@xr.register_dataset_accessor('fileio')
@xr.register_dataarray_accessor('fileio')
class FileIO:
    def __init__(self,xr_obj):
        self._obj=xr_obj
        
        self._pyhyper_type = 'reduced'
        try:
            self._chi_min = np.min(xr_obj.chi)
            self._chi_max = np.max(xr_obj.chi)
            self._chi_range = [self._chi_min,self._chi_max]
        except AttributeError:
            self._pyhyper_type = 'raw'
        
    def savePickle(self,filename):
        with open(filename, 'wb') as file:
            pickle.dump(self._obj, file)
            
    def sanitize_attrs(xr_obj):
        """
        Sanitize the attributes of an xarray object to make them JSON serializable,
        handling deeply nested dictionaries, lists, and array-like objects.
    
        Parameters:
        xr_obj (xarray.DataArray or xarray.Dataset): The xarray object to sanitize.
    
        Returns:
        xarray.DataArray or xarray.Dataset: A copy of the input object with sanitized attributes.
        """
        def sanitize_value(value):
            """Recursively sanitize a value to ensure JSON serializability."""
            if isinstance(value, datetime):
                return value.isoformat()  # Convert datetime to ISO 8601 string
            elif isinstance(value, np.ndarray):
                return value.tolist()  # Convert numpy arrays to lists
            elif hasattr(value, "__array__"):  # Handles other array-like objects
                return np.asarray(value).tolist()
            elif isinstance(value, dict):
                # Recursively sanitize dictionary values
                return {k: sanitize_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                # Recursively sanitize list elements
                return [sanitize_value(v) for v in value]
            else:
                try:
                    # Check if the value can be serialized to JSON
                    json.dumps(value)
                    return value
                except (TypeError, OverflowError):
                    return None  # Mark non-serializable values as None
    
        sanitized_obj = xr_obj.copy()
        sanitized_attrs = {}
        dropped_attrs = {}
    
        for key, value in sanitized_obj.attrs.items():
            sanitized_value = sanitize_value(value)
            if sanitized_value is not None:
                sanitized_attrs[key] = sanitized_value
            else:
                dropped_attrs[key] = value
    
        sanitized_obj.attrs = sanitized_attrs
    
        # Print or log a summary of the sanitized attributes
        if dropped_attrs:
            print("Dropped non-serializable attributes:")
            for key, value in dropped_attrs.items():
                print(f"  {key}: {type(value)} - {value}")
        else:
            print("No attributes were dropped.")
    
        if sanitized_attrs:
            print("\nConverted attributes:")
            for key, value in sanitized_attrs.items():
                print(f"  {key}: {type(value)} -> {value}")
    
        return sanitized_obj
    def make_attrs_netcdf_safe(xr_obj):
        """
        Make the attributes of an xarray object safe for NetCDF by JSON-encoding
        dictionaries and other complex data types.
    
        Parameters:
        xr_obj (xarray.DataArray or xarray.Dataset): The xarray object to process.
    
        Returns:
        xarray.DataArray or xarray.Dataset: A copy of the input object with NetCDF-safe attributes.
        """
        def encode_complex(value):
            """
            Encode complex data types (like dicts) into JSON strings.
            """
            if isinstance(value, (dict, list, tuple)):
                try:
                    # Convert to a JSON string
                    return json.dumps(value)
                except (TypeError, OverflowError) as e:
                    # Handle unexpected cases gracefully
                    print(f"Error encoding attribute value: {value} ({e})")
                    return None
            return value
    
        sanitized_obj = xr_obj.copy()
        encoded_attrs = {}
    
        for key, value in sanitized_obj.attrs.items():
            encoded_value = encode_complex(value)
            if encoded_value is not None:
                encoded_attrs[key] = encoded_value
            else:
                print(f"Dropping unsupported attribute: {key} -> {value}")
    
        sanitized_obj.attrs = encoded_attrs

        return sanitized_obj

    # - This was copied from the Toney group contribution for GIWAXS.
    def saveZarr(self,  filename, mode: str = 'w'):
        """
        Save the DataArray as a .zarr file in a specific path, with a file name constructed from a prefix and suffix.
         Parameters:
            da (xr.DataArray): The DataArray to be saved.
            base_path (Union[str, pathlib.Path]): The base path to save the .zarr file.
            prefix (str): The prefix to use for the file name.
            suffix (str): The suffix to use for the file name.
            mode (str): The mode to use when saving the file. Default is 'w'.
        """
        da = self._obj
        ds = da.to_dataset(name='DA')
        ds = self.sanitize_attrs(ds)
        # unstack any multiindexes on the array
        if hasattr(da, "indexes"):
            multiindexes = [dim for dim in da.indexes if isinstance(da.indexes[dim], xr.core.indexes.MultiIndex)]
        da = da.unstack(multiindexes) if multiindexes else da
        
        file_path = pathlib.Path(filename)
        ds.to_zarr(file_path, mode=mode)
    def saveNetCDF(self,  filename):
        """
        Save the DataArray as a netcdf file in a specific path, with a file name constructed from a prefix and suffix.

         Parameters:
             da (xr.DataArray): The DataArray to be saved.
             base_path (Union[str, pathlib.Path]): The base path to save the .zarr file.
             prefix (str): The prefix to use for the file name.
             suffix (str): The suffix to use for the file name.
             mode (str): The mode to use when saving the file. Default is 'w'.
        """
        da = self._obj
        # sanitize attrs and make netcdf safe by converting dicts to json strings
        da = self.sanitize_attrs(da)
        da = self.make_attrs_netcdf_safe(da)
        # unstack any multiindexes on the array
        if hasattr(da, "indexes"):
            multiindexes = [dim for dim in da.indexes if isinstance(da.indexes[dim], xr.core.indexes.MultiIndex)]
        da = da.unstack(multiindexes) if multiindexes else da
        file_path = pathlib.Path(filename)
        da.to_netcdf(file_path)
              
    def saveNexus(self,fileName,compression=5):
        data = self._obj
        timestamp = datetime.datetime.now()
        # figure out if xr is a raw or integrated array
        
        axes = list(data.indexes.keys())
        array_to_save = data.variable.to_numpy()
        dims_of_array_to_save = data.variable.dims
    
        dim_to_index = {}
        index_to_dim = {}
        
        for n,dim in enumerate(dims_of_array_to_save):
            dim_to_index[dim] = n
            index_to_dim[n] = dim
        
        if 'pix_x' in axes:
            self.pyhyper_type='raw'
            nonspatial_coords = axes
            nonspatial_coords.remove('pix_x')
            nonspatial_coords.remove('pix_y')
        elif 'qx' in axes:
            self.pyhyper_type='qxy'
            nonspatial_coords = axes
            nonspatial_coords.remove('qx')
            nonspatial_coords.remove('qy')
        elif 'chi' in axes:
            self.pyhyper_type='red2d'
            nonspatial_coords = axes
            nonspatial_coords.remove('chi')
            nonspatial_coords.remove('q')
        elif 'q' in axes:
            self.pyhyper_type='red1d'
            nonspatial_coords = axes
            nonspatial_coords.remove('q')
        else:
            raise Exception(f'Invalid PyHyper_type {self.pyhyper_type}.  Cannot write Nexus.')
        raw_axes = list(data.indexes.keys())
            
            # create the HDF5 NeXus file
        with h5py.File(fileName, "w") as f:
            # point to the default data to be plotted
            f.attrs[u'default']          = u'entry'
            # give the HDF5 root some more attributes
            f.attrs[u'file_name']        = fileName
            f.attrs[u'file_time']        = str(timestamp)
            #f.attrs[u'instrument']       = u'CyRSoXS v'
            f.attrs[u'creator']          = u'PyHyperScattering NeXus writer'
            f.attrs[u'creator_version']  = phs_version
            f.attrs[u'NeXus_version']    = u'4.3.0'
            f.attrs[u'HDF5_version']     = six.u(h5py.version.hdf5_version)
            f.attrs[u'h5py_version']     = six.u(h5py.version.version)

            # create the NXentry group
            nxentry = f.create_group(u'entry')
            nxentry.attrs[u'NX_class'] = u'NXentry'
            nxentry.attrs[u'canSAS_class'] = u'SASentry'
            nxentry.attrs[u'default'] = u'data'
            #nxentry.create_dataset(u'title', data=u'SIMULATION NAME GOES HERE') # do we have a sample name field?

            #setup general file stuff
            nxdata = nxentry.create_group(u'sasdata')
            nxdata.attrs[u'NX_class'] = u'NXdata'
            nxdata.attrs[u'canSAS_class'] = u'SASdata'
            nxdata.attrs[u'canSAS_version'] = u'0.1' #required for Nika to read the file.
            nxdata.attrs[u'signal'] = u'I'      # Y axis of default plot
                

            
            '''if self.pyhyper_type == 'raw':
                nxdata.attrs[u'I_axes'] = u'pix_x,pix_y'         # X axis of default plot
                nxdata.attrs[u'Q_indices'] = f'[{dim_to_index["pix_x"]},{dim_to_index["pix_y"]}]'               
            else:
                if self.pyhyper_type == 'qxy':
                    nxdata.attrs[u'I_axes'] = u'Qx,Qy'         # X axis of default plot
                    nxdata.attrs[u'Q_indices'] = f'[{dim_to_index["Qx"]},{dim_to_index["Qy"]}]'  
                elif self.pyhyper_type == 'red2d':
                    nxdata.attrs[u'I_axes'] = u'q,chi'         # X axis of default plot
                    nxdata.attrs[u'Q_indices'] = f'[{dim_to_index["q"]},{dim_to_index["chi"]}]' 
                elif self.pyhyper_type == 'red1d':
                    nxdata.attrs[u'I_axes'] = u'q'         # X axis of default plot
                    nxdata.attrs[u'Q_indices'] = f'[{dim_to_index["q"]}]' 
                else:
                    raise Exception(f'Invalid PyHyper_type {self.pyhyper_type}.  Cannot write Nexus.')
            '''
            
            ds = nxdata.create_dataset(u'I', data=array_to_save,compression=compression)
            ds.attrs[u'units'] = u'arbitrary'
            ds.attrs[u'long_name'] = u'Intensity (arbitrary units)'    # suggested X axis plot label
            # the following are to enable compatibility with Nika canSAS loading
           # ds.attrs[u'signal'] = 1
            #ds.attrs[u'axes'] = u'Qx,Qy'
            I_axes = '['
            Q_indices = '['
            for axis in raw_axes:
                I_axes += f'{axis},'
                Q_indices += f'{dim_to_index[axis]},'
                if type(data.indexes[axis]) == pandas.core.indexes.multi.MultiIndex:
                    idx = data.indexes[axis]
                    I_axes = I_axes[:-1]+'('
                    lvls = idx.levels
                    multiindex_arrays = defaultdict(list)
                    for row in idx:
                        for n,level in enumerate(lvls):
                            multiindex_arrays[level.name].append(row[n])
                    for level in lvls:
                        ds = nxdata.create_dataset(level.name, data=multiindex_arrays[level.name])
                        I_axes += f'{level.name};'
                        ds.attrs[u'PyHyper_origin'] = axis
                    I_axes = I_axes[:-1]+'),'
                else:
                    ds = nxdata.create_dataset(data.indexes[axis].name, data=data.indexes[axis].values)
                    if 'q' in axis:
                        ds.attrs[u'units'] = u'1/angstrom'
                    elif 'chi' in axis:
                        ds.attrs[u'units'] = u'degree'
                    #ds.attrs[u'long_name'] = u'Qx (A^-1)'    # suggested Y axis plot label
            I_axes = I_axes[:-1]+']'
            Q_indices = Q_indices[:-1]+']'
            nxdata.attrs[u'I_axes'] = I_axes
            nxdata.attrs[u'Q_indices'] = Q_indices
                        
            residual_attrs = nxentry.create_group(u'attrs')
            residual_attrs = self._serialize_attrs(residual_attrs,data.attrs.items())
            '''for k,v in data.attrs.items():
                print(f'Serializing {k}...')
                print(f'Data: type {type(v)}, data {v}')
                if type(v)==datetime.datetime:
                    ds = residual_attrs.create_dataset(k,data=v.strftime('%Y-%m-%dT%H:%M:%SZ'))
                    ds.attrs['phs_encoding'] = 'strftime-%Y-%m-%dT%H:%M:%SZ'
                elif type(v)==dict:
                    ds = residual_attrs.create_group(k)
                    
                else:
                    try:
                        residual_attrs.create_dataset(k, data=v)
                    except TypeError:
                        ds = residual_attrs.create_dataset(k, data=json.dumps(v))
                        ds.attrs['phs_encoding'] = 'json'
            '''
        print("wrote file:", fileName)

    def _serialize_attrs(self,parent,items):
        for k,v in items:
            #print(f'Serializing {k}...')
            #print(f'Data: type {type(v)}, data {v}')
            if type(v)==datetime.datetime:
                ds = parent.create_dataset(k,data=v.strftime('%Y-%m-%dT%H:%M:%SZ'))
                ds.attrs['phs_encoding'] = 'strftime-%Y-%m-%dT%H:%M:%SZ'
            elif type(v)==dict:
                grp = parent.create_group(k)
                grp.attrs['phs_encoding'] = 'dict-expanded'
                grp = self._serialize_attrs(grp,v.items())
            else:
                try:
                    parent.create_dataset(k, data=v)
                except TypeError:
                    try:
                        ds = parent.create_dataset(k, data=json.dumps(v))
                        ds.attrs['phs_encoding'] = 'json'
                    except TypeError:
                        warnings.warn('Failed to serialize {k} with type {type(v)} and value {v} as JSON.  Skipping.',stacklevel=2)
        return parent
        
def loadPickle(filename):
    return pickle.load( open( filename, "rb" ) )

def loadNexus(filename):
    with h5py.File(filename, "r") as f:    
        ds = xr.DataArray(f['entry']['sasdata']['I'],
                  dims=_parse_Iaxes(f['entry']['sasdata'].attrs['I_axes']),
                 coords = _make_coords(f))

        
        loaded_attrs = _unserialize_attrs(f['entry']['attrs'],{})
        
        '''        for entry in f['entry']['attrs']:
            #print(f'Processing attribute entry {entry}')
            try:
                encoding = f['entry']['attrs'][entry].attrs['phs_encoding']
                #print(f'Found data with a labeled encoding: {encoding}')
                if encoding == 'json':
                    loaded_attrs[entry] = json.loads(f['entry']['attrs'][entry][()].decode())
                elif encoding == 'dict-expanded':
                    loaded_attrs[entry] = self.load_attrs(entry)
                elif 'strftime' in encoding:
                    loaded_attrs[entry] = datetime.datetime.strptime(str(f['entry']['attrs'][entry][()].decode()),
                                                           encoding.replace('strftime-',''))
                else:
                    warnings.warn(f'Unknown phs_encoding {encoding} while loading {entry}.  Possible version mismatch.  Loading as string.',stacklevel=2)
                    loaded_attrs[entry] = f['entry']['attrs'][entry][()]
            except KeyError:
                loaded_attrs[entry] = f['entry']['attrs'][entry][()]'''
        #print(f'Loaded: {loaded_attrs}')
        ds.attrs.update(loaded_attrs)

    return ds

def _unserialize_attrs(hdf,attrdict):
    for entry in hdf:
        #print(f'Processing attribute entry {entry}')
        try:
            encoding = hdf[entry].attrs['phs_encoding']
            #print(f'Found data with a labeled encoding: {encoding}')
            if encoding == 'json':
                attrdict[entry] = json.loads(hdf[entry][()].decode())
            elif encoding == 'dict-expanded':
                attrdict[entry] = _unserialize_attrs(hdf[entry],{})
            elif 'strftime' in encoding:
                attrdict[entry] = datetime.datetime.strptime(str(hdf[entry][()].decode()),
                                                       encoding.replace('strftime-',''))
            else:
                warnings.warn(f'Unknown phs_encoding {encoding} while loading {entry}.  Possible version mismatch.  Loading as string.',stacklevel=2)
                attrdict[entry] = hdf[entry][()]
        except KeyError:
            attrdict[entry] = hdf[entry][()]        
    return attrdict
def _parse_Iaxes(axes,suppress_multiindex=True):
    axes = axes.replace('[','').replace(']','')
    axes_parts = axes.split(',')
    axes = []
    if suppress_multiindex:
        for part in axes_parts:
            if '(' in part:
                #print(f'multiindex: {part}')
                part = part.split('(')[0]
                #print(f'set part to {part}')
            axes.append(part)
    else:
        axes = axes_parts
    return axes

def _parse_multiindex_Iaxes(axis):
    axis = axis.replace(')','')
    axis = axis.split('(')[1]
    return axis.split(';')

def _make_coords(f):
    axes = _parse_Iaxes(f['entry']['sasdata'].attrs['I_axes'],suppress_multiindex=True)
    axes_raw = _parse_Iaxes(f['entry']['sasdata'].attrs['I_axes'],suppress_multiindex=False)

    coords = {}
    for n,axis in enumerate(axes_raw):
        if '(' in axis:
            levels = _parse_multiindex_Iaxes(axis)
            vals = []
            names = []
            for level in levels:
                names.append(level)
                vals.append(f['entry']['sasdata'][level])
            #print(names)
            #print(vals)
            coords[axes[n]] = pandas.MultiIndex.from_arrays(vals,names=names)
        else:
            coords[axes[n]] = f['entry']['sasdata'][axis]

    return coords
