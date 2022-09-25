import pandas as pd
import numpy as np
import streamlit as st
import datetime
import time
from st_clickable_images import clickable_images

def save_data(species: str, observer: str, location: str, observation_date: datetime, comment: str):
    """ Function for annotating entered data """
    # Display a warning if the user entered not all required values
    if (species == ""):
        st.warning("No species observation given. Please remember to tick the checkbox of the respective species "
        +"before form submission. The data were not annotated. Please enter them again.")
    elif (observer == ""):
        st.warning("No observer name given. Please enter your name in the 'Observer' field of the form "
        +"before form submission. The data were not annotated. Please enter them again.")
    elif(location == ""):
        st.warning("No location given. Please enter a description of the location in the 'Location' field of the "
        +"form before form submission. The data were not annotated. Please enter them again.")
    else:
        # Write data to file
        output_str = species+"\t"+observer+"\t"+location+"\t"+str(observation_date)+"\t"+comment+"\n"
        with open("./annotated_species.txt", "a") as out_file:
            out_file.write(output_str)


def increment_counter():
    """Incremention session state value"""
    st.session_state.counter += 1

# Function from https://gist.github.com/treuille/2ce0acb6697f205e44e3e0f576e810b7
def paginator(label, items, items_per_page=50):
    """Lets the user paginate a set of items.
    Parameters
    ----------
    label : str
        The label to display over the pagination widget.
    items : Iterator[Any]
        The items to display in the paginator.
    items_per_page: int
        The number of items to display per page.
    on_sidebar: bool
        Whether to display the paginator widget on the sidebar.
        
    Returns
    -------
    Iterator[Tuple[int, Any]]
        An iterator over *only the items on that page*, including
        the item's index.
    """

    # Display a pagination selectbox in the specified location.
    items = list(items)
    n_pages = len(items)
    n_pages = (len(items) - 1) // items_per_page + 1
    page_format_func = lambda i: "Page %s" % i
    page_number = st.sidebar.selectbox(label, range(n_pages), format_func=page_format_func)

    # Iterate over the items in the page to let the user display them.
    min_index = page_number * items_per_page
    max_index = min_index + items_per_page
    import itertools
    return itertools.islice(enumerate(items), min_index, max_index)


# Formatting
st.set_page_config(
    page_title='PhyloMatcher',
    layout='wide',
    page_icon=':fish:',
    initial_sidebar_state="collapsed",
)


if __name__ == '__main__':
    # Handle session
    if 'counter' not in st.session_state:
        st.session_state.counter = 0

    # Remove space at top of page
    st.markdown('<style>div.block-container{padding-top:0.5rem;}</style>', unsafe_allow_html=True)

    # Add filters/input widgets with tooltips
    st.sidebar.markdown("<b>Filters:</b>", unsafe_allow_html=True)
    selected_group = st.sidebar.radio("Oganism group: ", options=('Bony fish', 'Sea squirts', 'Whales', 'Cnidaria', \
        'Echinodermata', 'Bivalvia', 'Demospongiae', 'Gastropods', 'Polychaetes', 'Gymnolaemata', 'Hexapods', \
        'Malacostraca', 'Copepods', 'Branchiopoda', 'Other'), index=0)
    st.sidebar.markdown("#")

    # Header
    st.markdown("<h1><font color='darkblue'>Marine Organisms in the region of Aguilas</font></h1>", unsafe_allow_html=True)
    st.write("The marine organisms listed below have been observed in the region of Aguilas in the past. "
            +"Please look through the list of organisms and read the information given on the linked pages. ")
    st.write("The group of marine Chordata (fish) is displayed per default. Other groups can be displayed by secting "
            "the radio button of the a group of the sidebar.")
    st.write("In order to keep the loading time low only 50 images are shown on a page. You can switch between pages "
             "by selecting the corresponding page from the drop-down list in the sidebar")

    # Read information from individual files with meta-information
    file_names = ["Chordata_without_avis", "Arthropoda", "Bryozoa_and_Annelida", "Cnidaria_and_Echinodermata", "Mollusca_and_Porifera"]
    dfs = []
    for file_name in file_names:
        dfs.append(pd.read_csv("./"+file_name+"_v2.txt", sep="\t"))
    # Concatenate dataframes into one dataframe
    df_all_data = pd.concat(dfs, ignore_index=True)

    # Filtering
    assoc_dict = {"Bony fish" : "Actinopteri", \
                "Sea squirts": "Ascidiacea", \
                "Whales": "Mammalia", \
                "Cnidaria": "Cnidaria", \
                "Echinodermata": "Echinodermata", \
                "Bivalvia": "Bivalvia", \
                "Demospongiae": "Demospongiae", \
                "Gastropods": "Gastropoda", \
                "Polychaetes": "Polychaeta", \
                "Gymnolaemata": "Gymnolaemata", \
                "Hexapods": "Hexapoda", \
                "Malacostraca": "Malacostraca", \
                "Copepods": "Copepoda", \
                "Branchiopoda": "Branchiopoda", \
                "Other": "other"}
    groups = ["Actinopteri", "Ascidiacea", "Mammalia", "Cnidaria", "Echinodermata", "Bivalvia", \
            "Demospongiae", "Gastropoda", "Polychaeta", "Gymnolaemata", "Hexapoda", "Malacostraca", \
            "Copepoda", "Branchiopoda", "other"]
    if assoc_dict[selected_group] != "other":
        df_all_data = df_all_data.loc[df_all_data["Group"]==assoc_dict[selected_group], :]
    else:
        df_all_data = df_all_data.loc[~df_all_data["Group"].isin(groups), :]

    # Read NCBI information
    dfs_ncbi = []
    for file_name in file_names:
        df_ncbi = pd.read_csv("./"+file_name+"_NCBItaxreport.txt", sep="|", engine="python")
        df_ncbi = df_ncbi.drop("code\t" ,axis=1)
        if file_name == "Chordata_without_avis":
            df_ncbi = df_ncbi.drop("\tprimary taxid\t" ,axis=1)
            df_ncbi = df_ncbi.rename(columns={"\ttaxid\t": "taxid", "\ttaxname": "taxname"})
            df_ncbi["taxname"] = df_ncbi["taxname"].replace(to_replace ='\t', value = '', regex=True)
        else:
            df_ncbi = df_ncbi.drop("\tpreferred name\t" ,axis=1)
            df_ncbi = df_ncbi.rename(columns={"\ttaxid": "taxid", "\tname\t": "taxname"})
            df_ncbi["taxname"] = df_ncbi["taxname"].replace(to_replace ='\t', value = '', regex=True)
            df_ncbi["taxid"] = df_ncbi["taxid"].replace(to_replace ='\t', value = '', regex=True)
        dfs_ncbi.append(df_ncbi)
    df_ncbi_all = pd.concat(dfs_ncbi, ignore_index=True)

    # Define columns
    #for i,row in df_all_data.groupby(np.arange(len(df_all_data))//6):
    image_links = list(df_all_data["ImageLink"])
    species_names = list(df_all_data["Species"])

    st.sidebar.markdown("<b>Pages with images:</b>", unsafe_allow_html=True)
    image_iterator = paginator("Select a page", image_links)
    indices_on_page, images_on_page = map(list, zip(*image_iterator))

    clicked = clickable_images( images_on_page, indices_on_page,\
                                div_style={"display": "flex", "justify-content": "center", "flex-wrap": "wrap"}, \
                                img_style={"margin": "10px", "width": "150px"})
 
    # Display detailed information upon click
    if clicked > -1:
        page_number = (max(indices_on_page)+1)/50
        if page_number > 1:
            clicked = int(clicked + ((page_number-1)*50))
        # Make sure that there is some space before the detailed species information
        st.markdown("#")
        st.markdown("#")

        # Display detailed sepcies information
        st.subheader(df_all_data.iloc[clicked, 0])
        st.image(df_all_data.iloc[clicked, 2], width=600)
    
        # Link to GBIF
        worms_link='WoRMS: [Link]({link})'.format(link="https://www.marinespecies.org/aphia.php?p=taxdetails&id="+str(df_all_data.iloc[clicked, 1]))
        st.markdown(worms_link, unsafe_allow_html=True)
        # Link to NCBI
        df_tmp = df_ncbi_all.loc[df_ncbi_all["taxname"]==df_all_data.iloc[clicked, 0], :]
        if not(df_tmp.empty):
            ncbi_link='NCBI Taxonomy: [Link]({link})'.format(link="https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?mode=Info&id="+str(list(df_tmp["taxid"])))
            st.markdown(ncbi_link, unsafe_allow_html=True)