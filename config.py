SEPARATE_PUBLIST = False
USE_LINKS = False

OMIT_SECTIONS =  ['press_releases']

GOOGLE_SHEET = "Activity Tracker"

# CONTACT AND PERSONAL INFORMATION
INSTITUTION_URL = r"sese.asu.edu"
DEPARTMENT_NAME = r"School of Earth and Space Exploration"
INSTITUTION_NAME= r"Arizona State University"
INSTITUTION_STREET = r'781 Terrace Mall'
INSTITUTION_LOCATION = r'Tempe, AZ, 85287'
INSTITUTION_COUNTRY = r'USA'

FIRSTNAME = "Steven"
SURNAME = "Murray"
PHONE_NUMBER = r'+1 (480) 343 9188'
EMAIL = r'steven.g.murray@asu.edu'
CITIZENSHIP = [r"Australia"]


REFERENCES = [
    {
        "name": "Prof. Judd Bowman",
        "email": "judd.bowman@asu.edu",
        "address": "ASU School of Earth and Space Exploration PO Box 876004",
        "phone": "(+1)480 965-8880"
    },
    {
        "name": "Dr. Cathryn Trott",
        "email": "cathryn.trott@curtin.edu.au",
        "address": "ICRAR, Curtin University, 1 Turner Ave., Bentley, WA, 6102, Australia.",
        "phone": "(+61)8 9266 1306"
    },
    {
        "name": "Prof. Andrei Mesinger",
        "email": "andrei.mesinger@sns.it",
        "address": "Scuola Normale Superior, Piazza dei Cavalieri 7, Pisa, Italy",
        "phone": "(+39) 050 509 688"
    },
    {
        "name": "Dr. Danny Jacobs",
        "email": "dcjacob2@asu.edu",
        "address": "ASU School of Earth and Space Exploration PO Box 876004",
        "phone": "(+1)480 727-2227"
    },
    {
        "name": "Prof. Chris Power",
        "email": "chris.power@uwa.edu.au",
        "address": "ICRAR M468, The University of Western Australia, 35 Stirling Highway, "
                   "Crawley, WA 6009",
        "phone": "(+61)8 6488 7630"
    },
    {
        "name": "Prof. Peter Quinn",
        "email": "peter.quinn@uwa.edu.au",
        "address": "ICRAR M468, The University of Western Australia, 35 Stirling Highway, Crawley, WA 6009",
        "phone": "(+61)8 6488 4553"
    },
    {
        "name": "Dr. Aaron Robotham",
        "email": "aaron.robotham@icrar.org",
        "address": "ICRAR M468, The University of Western Australia, 35 Stirling Highway, Crawley, WA 6009",
        "phone": " (+61)8 6488 5564"
    },



]

# Maximum number of referrees to add to CV.
MAXREF = 3


WEBSITES = [
    {
        "url": r'https://steven-murray.github.io/',
        "kind": "web",
        "id": "steven-murray.github.io"
    },
    {
        "kind": 'linkedin',
        "id": 'steven-g-murray',
    },
    {
        "kind": 'github',
        "id": "steven-murray",
    },
]


RESEARCH_INTERESTS = {
    "21cm Cosmology":
        [
            'validation',
            "parameter inference",
            "statistical foreground modelling",
            "connecting instruments to theoretical predictions",
            'simulations',
        ],
    "Large-scale structure":
        [
            "halo mass function",
            "halo model",
            "warm dark matter",
            "fast synthetic catalogues"
        ],
    "Astrostatistics":
        [
            "hierarchical Bayesian models",
            "non-parametric statistics",
            "count distributions",
            "PCA"
        ],
    "Software and computing":
        [
            "high-standard development practices",
            "accessible web-applications for the community",
            "robust mathematical tools in Python"
        ]
}

KEEP_UNDERGRAD = True
KEEP_SECONDARY = False
KEEP_UNDERGRAD_COURSES = False

# Rating System for Jobs:
# 1 - non-academic job
# 2 - academic-related job (private tuition etc.)
# 3 - Academic minor job (class tuition, PhD)
# 4 - Academic Postdoc position
# 5 - Acadmic Fellowship
# 6+ - Better jobs.

JOB_MIN_RATING = 3
JOB_MIN_DATE = 2009
JOBS = [
    {"organisation": "Arizona State University",
     "city": "Tempe",
     "state": "Arizona",
     "title": "HERA/EDGES Postdoc",
     "dates": (2018, None),
     "rating": 4},


    {"organisation": "Curtin University",
     "city": "Perth",
     "state": "Western Australia",
     "title": "CAASTRO Postdoc",
     "dates": (2015, 2018),
     "rating": 4},

    {"organisation": "University of Western Australia",
     "city": "Perth",
     "state": "Western Australia",
     "title": "APA funded PhD student",
     "dates": (2012,2015),
     "rating": 3},

    {
        "organisation": "ICRAR/Pawsey",
        "city": "Perth",
        "state": "Western Australia",
        "title": "ICRAR/Pawsey Summer Internship",
        "dates": (2011, 2012),
        "rating": 3
    },

    {"organisation": "University of Western Australia",
     "city": "Perth",
     "state": "Western Australia",
     "title": "First-year Physics Lab Demonstration Tutor",
     "dates": (2011,),
     "rating": 3},

    {"organisation": "University of Queensland",
     "city": "Brisbane",
     "state": "Queensland",
     "title": "First-year Mathematics Tutor",
     "dates": (2009,),
     "rating": 3},

    {"organisation": "Private",
     "city": "Sunshine Coast",
     "state": "Queensland",
     "title": "Piano Tutor",
     "dates": (2004,2010),
     "rating": 1},

    {"organisation": "Private",
     "city": "Sunshine Coast",
     "state": "Queensland",
     "title": "Mathematics, Physics, Chemistry Tutor",
     "dates": (2006, 2010),
     "rating": 2},
]


# Academic Experience Modifiers
OMIT_GRANTS = False
OMIT_COLLABORATIONS = False
OMIT_COMMITTEES = False
OMIT_REFEREES = False
OMIT_LECTURING = False
OMIT_SUPERVISION = False
OMIT_TEACHING = False
OMIT_OUTREACH = False
OMIT_PROF_TRAINING = False
OMIT_PERSONAL_TRAINING = False
OMIT_INDUSTRY=False

# Awards Modifiers
AWARDS_MIN_YEAR = 2007
AWARDS_MIN_RATING = 2


GITHUB_USER = "steven-murray"
GITHUB_PWD = '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'
MAX_REPOS = 6
MAX_REPOS_COLLAB = 10
BLACKLIST = ['PyCosmology', "PyGS"]
BLACKLIST_ORGS = ['conda-forge', 'loco-lab']
MIN_CONTRIBUTIONS = 15

ORIGINAL_CODES = [
    'steven-murray/hankel', 
    'steven-murray/powerbox', 
    'halomod/TheHaloMod-SPA', 
    'halomod/halomod', 
    'halomod/hmf', 
    'steven-murray/yabf',
    'steven-murray/mrpy'
#    'steven-murray/beet-summarize'
]

ORCID = "0000-0003-3059-3823"
OTHER_BIBCODES = []
ACCEPTED = [
    '2021arXiv210912733S', 
    '2021arXiv210807282T',
    '2021arXiv210802263T',
    '2021arXiv210700018P',
    '2021arXiv210409547A',
]
HIGHLIGHT_CITE_PER_YEAR = 5

WRITE_POSTERS = False
WRITE_LOCAL_TALKS = False

DO_PROCEEDINGS = True

# Settings for determining which papers you are a "significant" contributor to
TOP_N = 4         # If you are in the TOP_N, you are always considered significant
ALPHABET_N = 12   # NUmber of authors required in alphabetical order to deem it an alphabetical collection of collaborators
                  # If you're not TOP_N and the paper has less than ALPHABET_N, you are not significant
                  # If there *is* ana alphabetical list, and you're before it, regardless of your author number,
                  # you are deemed significant.
