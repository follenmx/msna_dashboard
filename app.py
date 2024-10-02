import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import re

st.set_page_config(
    page_title="MSNA", page_icon="🧊", layout="wide", initial_sidebar_state="expanded"
)


sheet_id = st.secrets['data_link'] # Change to st.secret
csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

@st.cache_data
def load_data():
    df = pd.read_csv(csv_url)
    return df


df = load_data()
refresh_button = st.sidebar.button('Data Refresh')
if refresh_button:
    load_data.clear()  
    df = load_data() 
    
st.title("MSNA: Data Analysis")

# FILTERS
gender_filter = st.sidebar.multiselect(
    "Please select Gender",
    options=df["What is your sex?"].unique(),
    default=df["What is your sex?"].unique(),
)

age_filter = st.sidebar.multiselect(
    "Please select Age_group",
    options=df["Age_grp"].unique(),
    default=df["Age_grp"].unique(),
)

nationality_filter = st.sidebar.multiselect(
    "Please select Nationality",
    options=df["What is your citizenship?"].unique(),
    default=df["What is your citizenship?"].unique(),
)

legal_filter = st.sidebar.multiselect(
    "Please select Legal Status",
    options=df[
        "What is your current status (e.g., refugee, asylum seeker, etc.)?"
    ].unique(),
    default=df[
        "What is your current status (e.g., refugee, asylum seeker, etc.)?"
    ].unique(),
)

ethnic_filter = st.sidebar.multiselect(
    "Please select Ethnicity",
    options=df["Please specify what ethnic minority group"].unique(),
    default=df["Please specify what ethnic minority group"].unique(),
)

accomodation_filter = st.sidebar.multiselect(
    "Please select Accomodation",
    options=df["Do you currently live in a city or a village?"].unique(),
    default=df["Do you currently live in a city or a village?"].unique(),
)

# Filter query
df_query = (
    "`What is your sex?`.isin(@gender_filter) & "
    "`Age_grp`.isin(@age_filter) & "
    "`What is your citizenship?`.isin(@nationality_filter) & "
    "`What is your current status (e.g., refugee, asylum seeker, etc.)?`.isin(@legal_filter) & "
    "`Please specify what ethnic minority group`.isin(@ethnic_filter) & "
    "`Do you currently live in a city or a village?`.isin(@accomodation_filter)"
)
df = df.query(df_query)

total_submissions = len(df)
average_value = round(df["How many members are in your household, including you?"].mean(), 1)
max_value = df["How many members are in your household, including you?"].max()
kid_value = round(df["Of these, how many are children under 18?"].mean(), 1)
elderly_value = round(df["Of these, how many are senior citizens, aged over 60?"].mean(), 1)
age_value = round(df["What is your age?"].mean(), 1)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"**Total Submissions:** {total_submissions}")
with col2:
    st.markdown(f"**Avg household size:** {average_value}")
with col3:
    st.markdown(f"**Max household size:** {max_value}")

col4, col5, col6 = st.columns(3)
with col4:
    st.markdown(f"**Avg # of children in a household:** {kid_value}")
with col5:
    st.markdown(f"**Avg # of elderly in a household:** {elderly_value}")
with col6:
    st.markdown(f"**Avg age:** {age_value}")


def create_sex_distribution_pie_chart(df, column_name, fig_title):
    labels = df[column_name].value_counts().index
    values = df[column_name].value_counts().values

    # Create the pie chart
    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.4,  # Donut chart style
                textinfo="label+percent+value",  # Shows label, percent, and values
                insidetextorientation="horizontal",
            )
        ]
    )

    # Update layout for a transparent background and a professional look
    fig.update_layout(
        title=fig_title,
        paper_bgcolor="rgba(0,0,0,0)",  # Transparent background
        plot_bgcolor="rgba(0,0,0,0)",  # Transparent plot area
        showlegend=True,
    )

    return fig


def create_bar_chart(dataframe, column_name, chart_title):
    # Count the occurrences of each category in the specified column
    count_series = dataframe[column_name].value_counts().sort_values(ascending=False)
    count_df = count_series.reset_index()
    count_df.columns = [column_name, "Count"]

    # Create the bar chart
    fig = px.bar(
        count_df,
        x=column_name,
        y="Count",
        title=chart_title,
        labels={"Count": "Number of Responses", column_name: "Category"},
        text="Count",
    )

    # Update the layout for a professional look
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",  # Transparent plot background
        paper_bgcolor="rgba(0,0,0,0)",  # Transparent paper background
        font=dict(size=14),  # Font size for text
        title_font=dict(size=18),  # Font size for the title
        xaxis_title="Category",  # X-axis title
        yaxis_title="Number of Responses",  # Y-axis title
        hovermode="x",  # Hover mode
        bargap=0.2,  # Gap between bars
        height=600,  # Increase figure height
        margin=dict(b=150),  # Increase bottom margin for labels
    )
    fig.update_yaxes(range=[0, count_df["Count"].max() * 1.3])
    # Update the bar trace for a cleaner look
    fig.update_traces(
        marker_color="rgba(100, 149, 237, 0.6)",  # 'CornflowerBlue'
        marker_line_color="rgba(100, 149, 237, 1.0)",  # Bar border color
        marker_line_width=1.5,  # Bar border width
        opacity=0.9,  # Bar opacity
        textposition="outside",  # Position of the text labels
    )

    # Rotate x-axis labels to prevent overlap
    fig.update_layout(xaxis_tickangle=-45)

    return fig


def create_mbar_chart(df, column_name, option_list, bar_title):
    # Extract the relevant column
    column_data = df[column_name].dropna()

    # Initialize counts dictionary
    counts = {option: 0 for option in option_list}

    # Iterate over each response
    for response in column_data:
        for option in option_list:
            if option in response:
                counts[option] += 1

    # Convert the counts to a DataFrame
    df_counts = pd.DataFrame(list(counts.items()), columns=["Answer", "Count"])

    # Sort data for better visualization
    df_counts_sorted = df_counts.sort_values("Count", ascending=False)

    # Create the bar chart with a consistent color scheme
    fig = px.bar(
        df_counts_sorted,
        x="Answer",
        y="Count",
        text_auto=True,  # Automatically add text on bars
        title=bar_title,
        color="Answer",  # Color by answer
        color_discrete_sequence=px.colors.sequential.RdBu_r,  # Use a color scale
    )

    # Customize the chart layout
    fig.update_layout(
        xaxis_title="Options",
        yaxis_title="Count",
        plot_bgcolor="rgba(0,0,0,0)",  # Transparent background
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="black", size=12),  # Adjust font color and size for readability
        showlegend=False,  # Hide the legend if not necessary
        height=600,  # Increase figure height
        margin=dict(b=150),  # Increase bottom margin for labels
    )

    # Rotate x-axis labels to prevent overlap
    fig.update_layout(xaxis_tickangle=-45)

    # Customize bar appearance
    fig.update_traces(
        marker_line_color="rgb(8,48,107)",  # Bar border color
        marker_line_width=1.5,  # Width of the border
        opacity=0.8,
        textangle=0,  # Set text angle to 0 for horizontal alignment
    )

    return fig


def create_histogram(df, column_name, chart_title):
    # Ensure the data is numeric and drop NaN values
    data = pd.to_numeric(df[column_name], errors="coerce").dropna()

    # Determine the number of bins using Sturges' formula
    num_bins = int(np.ceil(1 + np.log2(len(data))))

    fig = px.histogram(data, x=data, nbins=num_bins, title=chart_title)
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",  # Transparent background
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis_title=column_name,
        yaxis_title="Count",
        height=500,
    )
    return fig


# Age Distribution
age_histogram_fig = create_histogram(df, "What is your age?", "Age Distribution")
st.plotly_chart(age_histogram_fig)

age_pie_chart_fig = create_sex_distribution_pie_chart(df, "Age_grp", "Age Distribution")
st.plotly_chart(age_pie_chart_fig)

# Nationality Distribution (Select Multiple)
nationality_options = ["Ukraine", "Moldova", "Romania", "Prefer not to say", "Other"]
nationality_bar_chart = create_mbar_chart(
    df, "What is your citizenship?", nationality_options, "Citizenship Distribution"
)
st.plotly_chart(nationality_bar_chart)

# Ethnicity Distribution
ethnicity_pie_chart_fig = create_sex_distribution_pie_chart(
    df,
    "Please specify what ethnic minority group",
    "Ethnicity Distribution",
)
st.plotly_chart(ethnicity_pie_chart_fig)

# Household Size Histogram
household_size_hist = create_histogram(
    df,
    "How many members are in your household, including you?",
    "Household Size Distribution",
)
st.plotly_chart(household_size_hist)

# Household Difficulty
household_difficulty_pie_chart = create_sex_distribution_pie_chart(
    df,
    "Are there other members in the household that have a lot of difficulty or cannot do any one of these actions?",
    "Household Difficulty",
)
st.plotly_chart(household_difficulty_pie_chart)


# Access Preventive Health Services
access_preventive_options = [
    "No difficulties",
    "Limited availability",
    "Lack of information",
    "High costs",
    "Long wait times",
    "Prefer not to say",
    "Other",
]
access_preventive_bar_chart = create_mbar_chart(
    df,
    "Preventive health services (e.g., vaccinations, health screenings)?",
    access_preventive_options,
    "Difficulties in Accessing Preventive Health Services",
)
st.plotly_chart(access_preventive_bar_chart)

# Access Reproductive Health Services
access_reproductive_options = [
    "No difficulties",
    "Limited availability",
    "Lack of specialists",
    "Cultural barriers",
    "High costs",
    "Prefer not to say",
    "Other",
]
access_reproductive_bar_chart = create_mbar_chart(
    df,
    "Reproductive health services and or pre and postnatal care?",
    access_reproductive_options,
    "Difficulties in Accessing Reproductive Health Services",
)
st.plotly_chart(access_reproductive_bar_chart)

# Access Necessary Medications
access_medicine_options = [
    "No difficulties",
    "Unavailable medications",
    "High costs",
    "Prescription issues",
    "Language barriers in understanding instructions",
    "Prefer not to say",
    "Other",
]
access_medicine_bar_chart = create_mbar_chart(
    df,
    "Necessary medications?",
    access_medicine_options,
    "Difficulties in Accessing Necessary Medications",
)
st.plotly_chart(access_medicine_bar_chart)

# How Medications are Procured
procure_medicine_pie_chart = create_sex_distribution_pie_chart(
    df,
    "How do you usually obtain the medications you need in Moldova?",
    "How Medications are Procured",
)
st.plotly_chart(procure_medicine_pie_chart)

# Health Insurance Coverage
have_coverage_pie_chart = create_sex_distribution_pie_chart(
    df,
    "Do you have any form of health insurance coverage in Moldova?",
    "Health Insurance Coverage",
)
st.plotly_chart(have_coverage_pie_chart)

# Impact of No Health Insurance
not_coverage_pie_chart = create_sex_distribution_pie_chart(
    df,
    "If not, has this affected your ability to access health services?",
    "Impact of No Health Insurance on Access",
)
st.plotly_chart(not_coverage_pie_chart)

# Sources of Health-Related Information
info_sources_options = [
    "Friends and relatives",
    "Internet/Mass Media",
    "Family doctor",
    "Prefer not to say",
    "Other (please specify)",
]
info_sources_bar_chart = create_mbar_chart(
    df,
    "Where do you typically get health-related information?",
    info_sources_options,
    "Sources of Health-Related Information",
)
st.plotly_chart(info_sources_bar_chart)

# Reliability of Health Information Sources
reliable_sources_pie_chart = create_sex_distribution_pie_chart(
    df,
    "Do you feel that you receive health information from accurate and reliable sources?",
    "Reliability of Health Information Sources",
)
st.plotly_chart(reliable_sources_pie_chart)

# Desired Health Information Topics
what_subjects_options = [
    "How to care for the health of older citizens",
    "How to care for the health of children",
    "Information on prevention and treatment of sexually transmitted diseases",
    "Information on prevention of chronic diseases",
    "Information on vaccination and access to vaccines",
    "How to care for family members with chronic diseases",
    "Myths and realities regarding health",
    "How to select adequate health sources",
    "Prefer not to say",
    "None of the above",
]
what_subjects_bar_chart = create_mbar_chart(
    df,
    "What health topics would you like to receive more information about?",
    what_subjects_options,
    "Desired Health Information Topics",
)
st.plotly_chart(what_subjects_bar_chart)

# Biggest Gaps in Healthcare Services
healthcare_gaps_options = [
    "Administrative barriers and bureaucracy",
    "Lack of family doctors in the area",
    "Lack of specialized doctors in the area",
    "Lack of laboratories or diagnostic imaging services",
    "No preventive care being offered",
    "Prefer not to say",
    "Other (please specify)",
]
healthcare_gaps_bar_chart = create_mbar_chart(
    df,
    "In your opinion, what are the biggest gaps in the provision of healthcare services in Moldova?",
    healthcare_gaps_options,
    "Biggest Gaps in Healthcare Services",
)
st.plotly_chart(healthcare_gaps_bar_chart)

# Satisfaction with Medical System
grade_social_healthcare_pie_chart = create_sex_distribution_pie_chart(
    df,
    "How satisfied are you in general with the medical system in Moldova?",
    "Satisfaction with Medical System",
)
st.plotly_chart(grade_social_healthcare_pie_chart)

# Safety and Security Concerns
safety_concern_options = [
    "None",
    "Physical threats or violence",
    "Verbal harassment or intimidation",
    "Theft or robbery",
    "Unsafe living conditions",
    "Limited access to health services",
    "Prefer not to say",
    "Other (please specify)",
]
safety_concern_bar_chart = create_mbar_chart(
    df,
    "Have you or members of your household faced any safety and security concerns since arriving in Moldova?",
    safety_concern_options,
    "Safety and Security Concerns",
)
st.plotly_chart(safety_concern_bar_chart)

# Support Systems for Safety Concerns
safety_support_options = [
    "Police",
    "Local authorities",
    "NGOs or humanitarian organizations",
    "Community leaders",
    "Friends or family",
    "Refugee support center",
    "Prefer not to say",
    "Other (please specify)",
]
safety_support_bar_chart = create_mbar_chart(
    df,
    "Where would you go to seek support in case of safety concerns? (Select all that apply)",
    safety_support_options,
    "Support Systems for Safety Concerns",
)
st.plotly_chart(safety_support_bar_chart)

# Experience of Discrimination
discrimination_pie_chart = create_sex_distribution_pie_chart(
    df,
    "During your stay in Moldova, have you or your family members experienced any forms of discrimination?",
    "Experience of Discrimination",
)
st.plotly_chart(discrimination_pie_chart)

# Most Vulnerable Groups
most_vulnerable_options = [
    "Children (under 18)",
    "Elderly (over 60)",
    "People with disabilities",
    "Single parents/caregivers",
    "Unaccompanied minors",
    "Ethnic or religious minorities",
    "Survivors of violence or torture",
    "People with chronic illnesses (physical or mental)",
    "Women and girls",
    "Persons dealing with substance abuse",
    "LGBTQ+ individuals",
    "Prefer not to say",
    "Other (please specify)",
]
most_vulnerable_bar_chart = create_mbar_chart(
    df,
    "In your opinion, which groups among refugees are the most vulnerable?",
    most_vulnerable_options,
    "Most Vulnerable Groups",
)
st.plotly_chart(most_vulnerable_bar_chart)

# Main Protection Risks for Women
women_challenge_options = [
    "Limited access to employment opportunities",
    "Balancing childcare responsibilities with work or education",
    "Gender-based violence or harassment",
    "Limited access to healthcare, including reproductive health services",
    "Social isolation and lack of community support",
    "Difficulties in accessing education or skill development programs",
    "Prefer not to say",
    "Other (please specify)",
]
women_challenge_bar_chart = create_mbar_chart(
    df,
    "What do you think are the main protection risks that refugee women face?",
    women_challenge_options,
    "Main Protection Risks for Women",
)
st.plotly_chart(women_challenge_bar_chart)

# Main Protection Risks for Men
men_challenge_options = [
    "Finding employment opportunities",
    "Accessing healthcare services",
    "Coping with psychological stress and trauma",
    "Legal issues (documentation, residency permits, etc.)",
    "Language barriers",
    "Separation from family members",
    "Prefer not to say",
    "Other (please specify)",
]
men_challenge_bar_chart = create_mbar_chart(
    df,
    "What are the main protection risks that refugee men face?",
    men_challenge_options,
    "Main Protection Risks for Men",
)
st.plotly_chart(men_challenge_bar_chart)

# Main Challenges for Children
children_challenge_options = [
    "Disruption of education",
    "Psychological trauma and stress",
    "Difficulty integrating into a new environment",
    "Language barriers",
    "Health and nutrition issues",
    "Loss of sense of security and stability",
    "Prefer not to say",
    "Other",
]
children_challenge_bar_chart = create_mbar_chart(
    df,
    "What do you think is the main challenge that refugee children are facing?",
    children_challenge_options,
    "Main Challenges for Children",
)
st.plotly_chart(children_challenge_bar_chart)

# Usual Support System
support_system_options = [
    "Family",
    "Friends",
    "Community - online support groups",
    "Community - offline support groups",
    "Prefer not to say",
    "Other",
]
support_system_bar_chart = create_mbar_chart(
    df,
    "What is your usual suppport system, to whom do you refer when you are faced with hardships?",
    support_system_options,
    "Usual Support System",
)
st.plotly_chart(support_system_bar_chart)

# Awareness of Gender-Based Violence Cases
gbv_cases_pie_chart = create_sex_distribution_pie_chart(
    df,
    "Are you aware of any incidents of gender-based violence among refugees in your community in Moldova?",
    "Awareness of Gender-Based Violence Cases",
)
st.plotly_chart(gbv_cases_pie_chart)

# Knowledge of Support for GBV
gbv_what_do_options = [
    "Police",
    "Hotline",
    "Shelter for survivors",
    "No",
    "Prefer not to answer",
    "Other",
]
gbv_what_do_bar_chart = create_mbar_chart(
    df,
    "Do you know where could a woman or young girl go for help in case of violence?",
    gbv_what_do_options,
    "Knowledge of Support for GBV",
)
st.plotly_chart(gbv_what_do_bar_chart)

# Need More Information on GBV Services
more_info_gbv_options = [
    "Health",
    "Shelter",
    "Psychological support",
    "Legal assistance",
    "Socio-Economic reintegration",
    "No",
    "Other",
]
more_info_gbv_bar_chart = create_mbar_chart(
    df,
    "Would you need more information about existing services for women affected by Violence?",
    more_info_gbv_options,
    "Need More Information on GBV Services",
)
st.plotly_chart(more_info_gbv_bar_chart)

# Need More Information on Child Protection Services
child_info_options = ["Psychological support", "Legal assistance", "No", "Other"]
child_info_bar_chart = create_mbar_chart(
    df,
    "Would you need more information about existing child protection services?",
    child_info_options,
    "Need More Information on Child Protection Services",
)
st.plotly_chart(child_info_bar_chart)

# Accessed MHPSS Services
mhpss_used_options = [
    "No",
    "Individual counseling sessions",
    "Group therapy or support groups",
    "Stress reduction and relaxation techniques",
    "Cultural adaptation and integration support",
    "Community-building activities and social events",
    "Educational workshops on mental health and well-being",
    "Crisis hotline or emergency mental health services",
    "Family counseling",
    "I don't know/Not sure",
    "Prefer not to say",
    "Other (please specify)",
]
mhpss_used_bar_chart = create_mbar_chart(
    df,
    "Have you or members of your household, accessed any mental health or psychosocial support services in Moldova?",
    mhpss_used_options,
    "Accessed MHPSS Services",
)
st.plotly_chart(mhpss_used_bar_chart)

# MHPSS Providers
mhpss_provider_options = [
    "Government health services",
    "International NGO",
    "Local NGO",
    "Private practitioner",
    "Remote services from Ukraine",
    "Religious organization",
    "Prefer not to say",
    "Other (please specify)",
]
mhpss_provider_bar_chart = create_mbar_chart(
    df,
    "From which source did you or your family members receive mental health and psychosocial support services?",
    mhpss_provider_options,
    "MHPSS Providers",
)
st.plotly_chart(mhpss_provider_bar_chart)

# Satisfaction with MHPSS Services
mhpss_quality_pie_chart = create_sex_distribution_pie_chart(
    df,
    "Are you satisfied with the quality of services received?",
    "Satisfaction with MHPSS Services",
)
st.plotly_chart(mhpss_quality_pie_chart)

# Helpful MHPSS Services
mhpss_helpful_options = [
    "Individual counseling sessions",
    "Group therapy or support groups",
    "Stress reduction and relaxation techniques",
    "Cultural adaptation and integration support",
    "Community-building activities and social events",
    "Educational workshops on mental health and well-being",
    "Crisis hotline or emergency mental health services",
    "Family counseling",
    "Prefer not to say",
    "Other",
]
mhpss_helpful_bar_chart = create_mbar_chart(
    df,
    "What type of psychosocial support do you think might be most helpful for the refugee community?",
    mhpss_helpful_options,
    "Helpful MHPSS Services",
)
st.plotly_chart(mhpss_helpful_bar_chart)

# Children Attending School
attend_school_pie_chart = create_sex_distribution_pie_chart(
    df, "Are your children currently attending school?", "Children Attending School"
)
st.plotly_chart(attend_school_pie_chart)

# Educational Support Needed
ed_support_options = [
    "Language classes",
    "Tutoring",
    "Psychological support",
    "Extracurricular activities",
    "None",
    "Prefer not to say",
    "Other",
]
ed_support_bar_chart = create_mbar_chart(
    df,
    "What additional support do you think children from the refugee community might need to succeed in school?",
    ed_support_options,
    "Educational Support Needed",
)
st.plotly_chart(ed_support_bar_chart)

# Impact of Online Schooling
ed_online_pie_chart = create_sex_distribution_pie_chart(
    df,
    "What are your thoughts on the impacts of online schooling on children?",
    "Impact of Online Schooling on Children",
)
st.plotly_chart(ed_online_pie_chart)

# Attempted to Find Employment
seek_employment_pie_chart = create_sex_distribution_pie_chart(
    df,
    "Have you attempted to find employment in Moldova?",
    "Attempted to Find Employment",
)
st.plotly_chart(seek_employment_pie_chart)

# Secured Employment
secure_employment_pie_chart = create_sex_distribution_pie_chart(
    df, "Were you able to secure employment?", "Secured Employment"
)
st.plotly_chart(secure_employment_pie_chart)

# Job Challenges Faced
job_challenge_options = [
    "No difficulties",
    "Language barriers",
    "Lack of recognition of qualifications or work experience",
    "Discrimination or prejudice from employers",
    "Lack of professional networks or connections",
    "Difficulty obtaining necessary work permits or documentation",
    "Cultural differences in workplace norms and expectations",
    "Prefer not to say",
    "Other (please specify)",
]
job_challenge_bar_chart = create_mbar_chart(
    df,
    "What challenges have you faced / are you facing in accessing the job market?",
    job_challenge_options,
    "Job Challenges Faced",
)
st.plotly_chart(job_challenge_bar_chart)

# Planning to Seek Employment
seek_employment_future_pie_chart = create_sex_distribution_pie_chart(
    df,
    "Are you planning to look for job in the coming months?",
    "Planning to Seek Employment",
)
st.plotly_chart(seek_employment_future_pie_chart)

# Support Needed for Employment
job_support_options = [
    "Language training specific to job-related terminology",
    "Vocational training or skill development programs",
    "Job search workshops (resume writing, interview skills)",
    "Job placement services or employment agencies",
    "Assistance with credential recognition and skill certification",
    "Entrepreneurship support and small business development programs",
    "Prefer not to say",
    "Other (please specify)",
]
job_support_bar_chart = create_mbar_chart(
    df,
    "What type of support do you think would be helpful for refugees in securing employment?",
    job_support_options,
    "Support Needed for Employment",
)
st.plotly_chart(job_support_bar_chart)

# Level of Interaction
interaction_pie_chart = create_sex_distribution_pie_chart(
    df,
    "How would you describe the level of interaction between Ukrainian refugees and the local Moldovan community?",
    "Level of Interaction with Local Community",
)
st.plotly_chart(interaction_pie_chart)

# Future Concerns
future_concern_options = [
    "Uncertainty about the future / lack of long-term stability",
    "Financial insecurity / difficulty making ends meet",
    "Limited employment opportunities",
    "Inadequate or temporary housing conditions",
    "Separation from family members",
    "Difficulties with language and communication",
    "Concerns about legal status or documentation",
    "Lack of social integration / feeling isolated",
    "Prefer not to say",
    "Other (please specify)",
]
future_concern_bar_chart = create_mbar_chart(
    df,
    "What are your biggest concerns about your future in Moldova?",
    future_concern_options,
    "Future Concerns",
)
st.plotly_chart(future_concern_bar_chart)

# Urgent Needs
urgent_need_options = [
    "Affordable and stable housing",
    "Access to healthcare services",
    "Employment opportunities",
    "Legal assistance and documentation support",
    "Education for children and youth",
    "Mental health and psychosocial support",
    "Financial assistance",
    "Integration support and community connections",
    "Prefer not to say",
    "Other (please specify)",
]
urgent_need_bar_chart = create_mbar_chart(
    df,
    "In your opinion, what is the most urgent need for refugees in Moldova right now?",
    urgent_need_options,
    "Urgent Needs",
)
st.plotly_chart(urgent_need_bar_chart)

# Future Plans
plans_options = [
    "Return to Ukraine as soon as possible",
    "Stay in Moldova until it's safe to return to Ukraine",
    "Relocate to another country to join family/contacts",
    "Stay in Moldova long-term, regardless of the war",
    "Undecided / Don't know yet",
    "Prefer not to say",
    "Other (please specify)",
]
plans_bar_chart = create_mbar_chart(
    df,
    "What are your future plans regarding the war?",
    plans_options,
    "Future Plans Regarding the War",
)
st.plotly_chart(plans_bar_chart)

if 'Age_grp' in df.columns and \
   'Please specify what ethnic minority group' in df.columns and \
   'Were you able to access the healthcare service you needed?' in df.columns:
   
    # Create a subset of the data
    heatmap_data = df[['Age_grp', 'Please specify what ethnic minority group', 'Were you able to access the healthcare service you needed?']]
    
    # Rename columns for ease
    heatmap_data = heatmap_data.rename(columns={
        'Age_grp': 'Age Group',
        'Please specify what ethnic minority group': 'Ethnicity',
        'Were you able to access the healthcare service you needed?': 'Accessed Healthcare'
    })
    
    # Drop rows with missing values in these columns
    heatmap_data = heatmap_data.dropna(subset=['Age Group', 'Ethnicity', 'Accessed Healthcare'])
    
    # For each combination of Age Group and Ethnicity, compute the proportion of 'Yes' responses
    pivot_table = heatmap_data.pivot_table(
        index='Ethnicity',
        columns='Age Group',
        values='Accessed Healthcare',
        aggfunc=lambda x: (x=='Yes').mean()
    )
    
    # Because the values are proportions, multiply by 100 to get percentages
    pivot_table = pivot_table * 100
    
    # Create the heatmap
    fig = px.imshow(
        pivot_table,
        labels=dict(x="Age Group", y="Ethnicity", color="Percentage of Access"),
        x=pivot_table.columns,
        y=pivot_table.index,
        color_continuous_scale='Viridis',
        text_auto=True
    )
    
    fig.update_layout(
        title="Heatmap: Correlation Between Age, Ethnicity, and Healthcare Access",
        xaxis_title="Age Group",
        yaxis_title="Ethnicity",
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent background
        paper_bgcolor='rgba(0,0,0,0)',
        height=600
    )
    
    st.plotly_chart(fig)


if 'Please specify what ethnic minority group' in df.columns and \
   'Do you currently live in a city or a village?' in df.columns and \
   'Were you able to access the healthcare service you needed?' in df.columns:
    
    # Prepare data
    facet_data = df[['Please specify what ethnic minority group',
                     'Do you currently live in a city or a village?',
                     'Were you able to access the healthcare service you needed?']].dropna()
    facet_data = facet_data.rename(columns={
        'Please specify what ethnic minority group': 'Ethnicity',
        'Do you currently live in a city or a village?': 'Location',
        'Were you able to access the healthcare service you needed?': 'Accessed Healthcare'
    })
    
    # Calculate counts
    facet_counts = facet_data.groupby(['Location', 'Ethnicity', 'Accessed Healthcare']).size().reset_index(name='Count')
    
    # Create the facet grid
    fig = px.bar(
        facet_counts,
        x='Ethnicity',
        y='Count',
        color='Accessed Healthcare',
        facet_col='Location',
        category_orders={"Location": sorted(facet_counts['Location'].unique())},
        title='Healthcare Access by Ethnicity and Location',
        labels={'Count': 'Number of Responses', 'Ethnicity': 'Ethnicity', 'Accessed Healthcare': 'Accessed Healthcare'},
        barmode='group'
    )
    
    fig.update_layout(
        height=600,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    st.plotly_chart(fig)


if 'Please specify what ethnic minority group' in df.columns and \
   'Age_grp' in df.columns and \
   'What prevented you from receiving the service?' in df.columns:
    
    # Prepare data
    treemap_data = df[['Please specify what ethnic minority group',
                       'Age_grp',
                       'What prevented you from receiving the service?']].dropna()
    treemap_data = treemap_data.rename(columns={
        'Please specify what ethnic minority group': 'Ethnicity',
        'Age_grp': 'Age Group',
        'What prevented you from receiving the service?': 'Healthcare Problems'
    })
    
    # List of predefined options
    healthcare_problems_options = [
        'Discrimination',
        'Long waiting times',
        'Lack of information about available services',
        'Lack of necessary documentation',
        'Lack of specialized services',
        'Transportation issues',
        'Cost of services',
        'Language barriers',
        'Prefer not to say',
        'Other (please specify)'
    ]
    
    # Function to extract problems from each response
    def extract_problems(response):
        # Split on commas or semicolons, accounting for possible whitespace
        problems = re.split(r'[;,]\s*', response)
        # Match problems to predefined options
        matched_problems = [problem.strip() for problem in problems if problem.strip() in healthcare_problems_options]
        return matched_problems
    
    # Apply the function to the 'Healthcare Problems' column
    treemap_data['Healthcare_Problems_List'] = treemap_data['Healthcare Problems'].apply(extract_problems)
    
    # Explode the list to have one problem per row
    treemap_data = treemap_data.explode('Healthcare_Problems_List')
    
    # Remove rows with empty problems (in case of unmatched problems)
    treemap_data = treemap_data.dropna(subset=['Healthcare_Problems_List'])
    
    # Group the data
    treemap_counts = treemap_data.groupby(['Ethnicity', 'Age Group', 'Healthcare_Problems_List']).size().reset_index(name='Count')
    
    # Create the treemap
    fig = px.treemap(
        treemap_counts,
        path=['Ethnicity', 'Age Group', 'Healthcare_Problems_List'],
        values='Count',
        color='Count',
        color_continuous_scale='Blues',
        title='Distribution of Healthcare Problems by Ethnicity and Age Group'
    )
    
    fig.update_layout(
        height=600,
        margin=dict(t=50, l=25, r=25, b=25),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig)


