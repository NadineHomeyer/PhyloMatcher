import pandas as pd
import streamlit as st
import datetime
import time


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

# Formatting
st.set_page_config(
    page_title='PhyloMatcher',
    layout='wide',
    page_icon=':fish:',
    initial_sidebar_state="collapsed"
)


if __name__ == '__main__':
    # Handle session
    if 'counter' not in st.session_state:
        st.session_state.counter = 0

    # Remove space at top of page
    st.markdown('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)

    # Add filters/input widgets with tooltips
    st.sidebar.markdown("Filters")
    selected_group = st.sidebar.radio("Oganism group: ", options=('bony fish', 'sea squirts', 'whales', 'other'), index=0)

    # Header
    st.markdown("<h1><font color='darkblue'>Marine Organisms in the region of Aguilas</font></h1>", unsafe_allow_html=True)
    st.write("The marine organisms listed below have been observed in the region of Aguilas in the past. "
            +"Please look through the list of organisms and read the information given on the linked pages. "
            +"If you are sure that you have identified an organism you have seen, please annotate it by clicking "
            +"onto the 'Annotate Organism' dropdown below the image, tick the checkbox beside the name of the "
            +"organism, fill in the requested information, and click onto the 'Submit' button. If the page refreshes"
            +"without a warning message the annotation was sucessful and you can annotate of the next organism.")
    # Read information from file with meta-information
    df = pd.read_csv("./Chordata_without_avis_v2.txt", sep="\t")
    # Filtering
    assoc_dict = {"bony fish" : "Actinopteri", "sea squirts": "Ascidiacea", "whales": "Mammalia", "other": "other"}
    groups = ["Actinopteri", "Ascidiacea", "Mammalia"]
    if assoc_dict[selected_group] != "other":
        df = df.loc[df["Group"]==assoc_dict[selected_group], :]
    else:
        df = df.loc[~df["Group"].isin(groups), :]

    # Read NCBI information
    df_ncbi = pd.read_csv("./Chordata_without_Avis_NCBItaxreport.txt", sep="|", engine="python")
    df_ncbi = df_ncbi.drop("code\t" ,axis=1)
    df_ncbi = df_ncbi.drop("\tprimary taxid\t" ,axis=1)
    df_ncbi = df_ncbi.rename(columns={"\ttaxid\t": "taxid", "\ttaxname": "taxname"})
    df_ncbi["taxname"] = df_ncbi["taxname"].replace(to_replace ='\t', value = '', regex=True)

    # Define columns
    pad1, col, pad2 = st.columns((4,6,4))

    with col:
        for i, row in df.iterrows():
            # Include Species name
            st.subheader(row["Species"])
            # Include Image
            st.image(row["ImageLink"], width=450)
            # Link to GBIF
            worms_link='WoRMS: [Link]({link})'.format(link="https://www.marinespecies.org/aphia.php?p=taxdetails&id="+str(row["AphisID"]))
            st.markdown(worms_link, unsafe_allow_html=True)
            # Link to NCBI
            df_tmp = df_ncbi.loc[df_ncbi["taxname"]==row["Species"], :]
            if not(df_tmp.empty):
                ncbi_link='NCBI Taxonomy: [Link]({link})'.format(link="https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?mode=Info&id="+str(list(df_tmp["taxid"])))
                st.markdown(ncbi_link, unsafe_allow_html=True)

            # Remove spaces from name before it can be using it as id
            spec_id = row["Species"].replace(" ", "")

            # Create form
            with st.expander("Annotate Observation"):
                with st.form("form_"+spec_id):
                    st.subheader("Observation Annotation Form:")
                    # Species Name
                    species_bool = st.checkbox(row["Species"]+"  was observed", key=spec_id, value=False)
                    species = ""
                    if species_bool:
                        species = row["Species"]
                    # Observer
                    observer = st.text_input("Observer: ", value="", key="obs_"+spec_id, help="Please enter your name")
                    # Location
                    location = st.text_input("Location where species was observed: ", value="Snorkeling event", key="loc_"+spec_id, \
                    help="If other location, please provide location details that allow a determination of its latitude and longitude.")
                    # Date
                    observation_date = st.date_input("Date of observation: ", value=datetime.datetime.now(), key="date_"+spec_id)
                    # Comment
                    comment = st.text_area("Comment: ", value="")

                    # Submit button
                    submitted = st.form_submit_button("Submit", on_click=increment_counter)
                    if submitted:
                        save_data(species, observer, location, observation_date, comment)
                        time.sleep(1)
                        st.experimental_rerun()

            st.write(" ")