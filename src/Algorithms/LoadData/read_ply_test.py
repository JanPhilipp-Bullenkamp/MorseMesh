
import collections
import numpy as np

from .Datastructure import Vertex, Simplex

# from ply specification, and additional dtypes found in the wild
_dtypes = {
    'char': 'i1',
    'uchar': 'u1',
    'short': 'i2',
    'ushort': 'u2',
    'int': 'i4',
    'int8': 'i1',
    'int16': 'i2',
    'int32': 'i4',
    'int64': 'i8',
    'uint': 'u4',
    'uint8': 'u1',
    'uint16': 'u2',
    'uint32': 'u4',
    'uint64': 'u8',
    'float': 'f4',
    'float16': 'f2',
    'float32': 'f4',
    'float64': 'f8',
    'double': 'f8'}

# Inverse of the above dict, collisions on numpy type were removed
_inverse_dtypes = {
    'i1': 'char',
    'u1': 'uchar',
    'i2': 'short',
    'u2': 'ushort',
    'i4': 'int',
    'i8': 'int64',
    'u4': 'uint',
    'u8': 'uint64',
    'f4': 'float',
    'f2': 'float16',
    'f8': 'double'}

def read_ply(filename, quality_index, vertices_dict, edges_dict, faces_dict, inverted=False):
    """! @brief Reads a ply file and writes the simplicial complex into vertices, edges and faces dictionaries.
    
    @details This function reads the given ply file and fills the given vertices dictionary, edges dictionary 
    and faces dictionary. It uses the values given at the quality index position as Morse function values and makes 
    sure that they are all unique so that we can use it for discrete Morse theory. Also allows to flip the function values
    by multiplying with -1 and thereby switching minima and maxima.
    
    @param filename The ply file to be read.
    @param quality_index The position of the quality you want to read in as the Morse function. Might vary depending on the
           ply file and application.
    @param vertices_dict The vertices dictionary to be filled with vertices.
    @param edges_dict The edges dictionary to be filled with edges.
    @param faces_dict The faces dictionary to be filled with faces.
    @param inverted Optional boolean: whether the Morse function values (quality values) should be multiplied with -1. 
           Doing this flips maxima and minima, default is False
    
    @return Despite filling the dictionaries, returns the minimum and maximum function value as min, max.
    """
    rawdata = PlyData.read(filename)
    
    vals = []
    for vindex, pt in enumerate(rawdata['vertex']):
        vert = Vertex(x=pt[0], y=pt[1], z=pt[2], quality=pt[quality_index], index=vindex)
        if inverted:
            vert.fun_val = -1 * vert.quality
        else:
            vert.fun_val = vert.quality
        vals.append(vert.fun_val)
        vertices_dict[vindex] = vert
        
    counts = Counter(vals)
    for vert in vertices_dict.values():
        if counts[vert.fun_val] > 1:
            tmp = vert.fun_val
            vert.fun_val = vert.fun_val + (counts[vert.fun_val] - 1) * 0.0000001
            counts[tmp] = counts[tmp] - 1
            
    
    eindex = 0
    unique_edges = set()
    for findex, rawface in enumerate(rawdata['face']):
        face = Simplex(indices=set(rawface[0]), index=findex)
        face.set_fun_val(vertices_dict)
        
        faces_dict[findex] = face
        
        for i in range(3):
            tmp = list(rawface[0])
            tmp_ind = tmp.pop(i)
            vertices_dict[tmp_ind].star["F"].append(findex)
            
            vertices_dict[tmp_ind].neighbors.add(tmp[0])
            vertices_dict[tmp_ind].neighbors.add(tmp[1])
            
            if set(tmp) not in unique_edges:
                edge = Simplex(indices=set(tmp), index=eindex)
                edge.set_fun_val(vertices_dict)
                
                edges_dict[eindex] = edge
                for tmp_ed_ind in tmp:
                    vertices_dict[tmp_ed_ind].star["E"].append(eindex)
                
                eindex+=1
                
                unique_edges.add(frozenset(tmp))
    return min(vals), max(vals)

def load_ply(file_obj,
             resolver=None,
             fix_texture=True,
             prefer_color=None,
             *args,
             **kwargs):
    """
    Load a PLY file from an open file object.
    Parameters
    ---------
    file_obj : an open file- like object
      Source data, ASCII or binary PLY
    resolver : trimesh.visual.resolvers.Resolver
      Object which can resolve assets
    fix_texture : bool
      If True, will re- index vertices and faces
      so vertices with different UV coordinates
      are disconnected.
    prefer_color : None, 'vertex', or 'face'
      Which kind of color to prefer if both defined
    Returns
    ---------
    mesh_kwargs : dict
      Data which can be passed to
      Trimesh constructor, eg: a = Trimesh(**mesh_kwargs)
    """

    # OrderedDict which is populated from the header
    elements, is_ascii = _parse_header(file_obj)

    # functions will fill in elements from file_obj
    if is_ascii:
        _ply_ascii(elements, file_obj)
    else:
        _ply_binary(elements, file_obj)

    # translate loaded PLY elements to kwargs
    kwargs = _elements_to_kwargs(
        elements=elements,
        fix_texture=fix_texture,
        prefer_color=prefer_color)

    return kwargs

def _parse_header(file_obj):
    """
    Read the ASCII header of a PLY file, and leave the file object
    at the position of the start of data but past the header.
    Parameters
    -----------
    file_obj : open file object
      Positioned at the start of the file
    Returns
    -----------
    elements : collections.OrderedDict
      Fields and data types populated
    is_ascii : bool
      Whether the data is ASCII or binary
    image_name : None or str
      File name of TextureFile
    """

    if 'ply' not in str(file_obj.readline()).lower():
        raise ValueError('Not a ply file!')

    # collect the encoding: binary or ASCII
    encoding = file_obj.readline().decode('utf-8').strip().lower()
    is_ascii = 'ascii' in encoding

    # big or little endian
    endian = ['<', '>'][int('big' in encoding)]
    elements = collections.OrderedDict()

    while True:
        raw = file_obj.readline()
        if raw is None:
            raise ValueError("Header not terminated properly!")
        raw = raw.decode('utf-8').strip()
        line = raw.split()

        # we're done
        if 'end_header' in line:
            break

        # elements are groups of properties
        if 'element' in line[0]:
            # we got a new element so add it
            name, length = line[1:]
            elements[name] = {
                'length': int(length),
                'properties': collections.OrderedDict()}
        # a property is a member of an element
        elif 'property' in line[0]:
            # is the property a simple single value, like:
            # `propert float x`
            if len(line) == 3:
                dtype, field = line[1:]
                elements[name]['properties'][
                    str(field)] = endian + _dtypes[dtype]
            # is the property a painful list, like:
            # `property list uchar int vertex_indices`
            elif 'list' in line[1]:
                dtype_count, dtype, field = line[2:]
                elements[name]['properties'][
                    str(field)] = (
                    endian +
                    _dtypes[dtype_count] +
                    ', ($LIST,)' +
                    endian +
                    _dtypes[dtype])

    return elements, is_ascii

def _ply_ascii(elements, file_obj):
    """
    Load data from an ASCII PLY file into an existing elements data structure.
    Parameters
    ------------
    elements : OrderedDict
      Populated from the file header, data will
      be added in-place to this object
    file_obj : file-like-object
      Current position at the start
      of the data section (past the header).
    """

    # get the file contents as a string
    text = str(file_obj.read().decode('utf-8'))
    # split by newlines
    lines = str.splitlines(text)
    # get each line as an array split by whitespace
    array = [np.fromstring(i, sep=' ') for i in lines]
    # store the line position in the file
    row_pos = 0

    # loop through data we need
    for key, values in elements.items():
        # if the element is empty ignore it
        if 'length' not in values or values['length'] == 0:
            continue
        data = array[row_pos:row_pos + values['length']]
        row_pos += values['length']
        # try stacking the data, which simplifies column-wise access. this is only
        # possible, if all rows have the same length.
        try:
            data = np.vstack(data)
            col_count_equal = True
        except ValueError:
            col_count_equal = False

        # number of list properties in this element
        list_count = sum(
            1 for dt in values['properties'].values() if '$LIST' in dt)
        if col_count_equal and list_count <= 1:
            # all rows have the same length and we only have at most one list
            # property where all entries have the same length. this means we can
            # use the quick numpy-based loading.
            element_data = _load_element_single(
                values['properties'], data)
        else:
            # there are lists of differing lengths. we need to fall back to loading
            # the data by iterating all rows and checking for list-lengths. this is
            # slower than the variant above.
            element_data = _load_element_different(
                values['properties'], data)

        elements[key]['data'] = element_data

def _load_element_single(properties, data):
    """
    Load element data with lists of a single length
    based on the element's property-definitions.
    Parameters
    ------------
    properties : dict
      Property definitions encoded in a dict where
      the property name is the key and the property
      data type the value.
    data : array
      Data rows for this element, if the data contains
      list-properties all lists belonging to one property
      must have the same length.
    """

    first = data[0]
    columns = {}
    current = 0
    for name, dt in properties.items():
        # if the current index has gone past the number
        # of items we actually have exit the loop early
        if current >= len(first):
            break
        if '$LIST' in dt:
            dtype = dt.split('($LIST,)')[-1]
            # the first entry in a list-property
            # is the number of elements in the list

            length = int(first[current])
            columns[name] = data[
                :, current + 1:current + 1 + length].astype(dtype)
            # offset by length of array plus one for each uint index
            current += length + 1
        else:
            columns[name] = data[:, current:current + 1].astype(dt)
            current += 1

    return columns

def _load_element_different(properties, data):
    """
    Load elements which include lists of different lengths
    based on the element's property-definitions.
    Parameters
    ------------
    properties : dict
      Property definitions encoded in a dict where the property name is the key
      and the property data type the value.
    data : array
      Data rows for this element.
    """
    edata = {k: [] for k in properties.keys()}
    for row in data:
        start = 0
        for name, dt in properties.items():
            length = 1
            if '$LIST' in dt:
                dt = dt.split('($LIST,)')[-1]
                # the first entry in a list-property is the number of elements
                # in the list
                length = int(row[start])
                # skip the first entry (the length), when reading the data
                start += 1
            end = start + length
            edata[name].append(row[start:end].astype(dt))
            # start next property at the end of this one
            start = end

    # if the shape of any array is (n, 1) we want to
    # squeeze/concatenate it into (n,)
    squeeze = {k: np.array(v, dtype='object')
               for k, v in edata.items()}
    # squeeze and convert any clean 2D arrays
    squeeze.update({k: v.squeeze().astype(edata[k][0].dtype)
                    for k, v in squeeze.items() if len(v.shape) == 2})

    return squeeze


def _ply_binary(elements, file_obj):
    """
    Load the data from a binary PLY file into the elements data structure.
    Parameters
    ------------
    elements : OrderedDict
      Populated from the file header.
      Object will be modified to add data by this function.
    file_obj : open file object
      With current position at the start
      of the data section (past the header)
    """

    def populate_listsize(file_obj, elements):
        """
        Given a set of elements populated from the header if there are any
        list properties seek in the file the length of the list.
        Note that if you have a list where each instance is different length
        (if for example you mixed triangles and quads) this won't work at all
        """
        p_start = file_obj.tell()
        p_current = file_obj.tell()
        elem_pop = []
        for element_key, element in elements.items():
            props = element['properties']
            prior_data = ''
            for k, dtype in props.items():
                prop_pop = []
                if '$LIST' in dtype:
                    # every list field has two data types:
                    # the list length (single value), and the list data (multiple)
                    # here we are only reading the single value for list length
                    field_dtype = np.dtype(dtype.split(',')[0])
                    if len(prior_data) == 0:
                        offset = 0
                    else:
                        offset = np.dtype(prior_data).itemsize
                    file_obj.seek(p_current + offset)
                    blob = file_obj.read(field_dtype.itemsize)
                    if len(blob) == 0:
                        # no data was read for property
                        prop_pop.append(k)
                        break
                    size = np.frombuffer(blob, dtype=field_dtype)[0]
                    props[k] = props[k].replace('$LIST', str(size))
                prior_data += props[k] + ','
            if len(prop_pop) > 0:
                # if a property was empty remove it
                for pop in prop_pop:
                    props.pop(pop)
                # if we've removed all properties from
                # an element remove the element later
                if len(props) == 0:
                    elem_pop.append(element_key)
                    continue
            # get the size of the items in bytes
            itemsize = np.dtype(', '.join(props.values())).itemsize
            # offset the file based on read size
            p_current += element['length'] * itemsize
        # move the file back to where we found it
        file_obj.seek(p_start)
        # if there were elements without properties remove them
        for pop in elem_pop:
            elements.pop(pop)

    def populate_data(file_obj, elements):
        """
        Given the data type and field information from the header,
        read the data and add it to a 'data' field in the element.
        """
        for key in elements.keys():
            items = list(elements[key]['properties'].items())
            dtype = np.dtype(items)
            data = file_obj.read(elements[key]['length'] * dtype.itemsize)
            try:
                elements[key]['data'] = np.frombuffer(
                    data, dtype=dtype)
            except BaseException:
                log.warning('PLY failed to populate: {}'.format(key))
                elements[key]['data'] = None
        return elements

    def _elements_size(elements):
        """
        Given an elements data structure populated from the header,
        calculate how long the file should be if it is intact.
        """
        size = 0
        for element in elements.values():
            dtype = np.dtype(','.join(element['properties'].values()))
            size += element['length'] * dtype.itemsize
        return size

    # some elements are passed where the list dimensions
    # are not included in the header, so this function goes
    # into the meat of the file and grabs the list dimensions
    # before we to the main data read as a single operation
    populate_listsize(file_obj, elements)

    # how many bytes are left in the file
    size_file = util.distance_to_end(file_obj)
    # how many bytes should the data structure described by
    # the header take up
    size_elements = _elements_size(elements)

    # if the number of bytes is not the same the file is probably corrupt
    if size_file != size_elements:
        raise ValueError('PLY is unexpected length!')

    # with everything populated and a reasonable confidence the file
    # is intact, read the data fields described by the header
    populate_data(file_obj, elements)