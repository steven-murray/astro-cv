import os

import config as c
import sections as sc
from structure import document


def compile_latex(fname):
    for _ in range(2):
        os.system(f"""pdflatex -synctex=1 -interaction=nonstopmode {fname} > {fname.replace("tex", 'log')}""")


if __name__ == "__main__":
    document = document.replace("{%firstname%}", c.FIRSTNAME)
    document = document.replace("{%surname%}", c.SURNAME)

    body = ""
    # Contact Info
    if "contact_information" not in c.OMIT_SECTIONS:
        body += sc.create_contact_information(
            institution_country=c.INSTITUTION_COUNTRY,
            institution_location=c.INSTITUTION_LOCATION,
            institution_name=c.INSTITUTION_NAME,
            institution_street=c.INSTITUTION_STREET,
            institution_url=c.INSTITUTION_URL,
            department_name=c.DEPARTMENT_NAME,
            phone_number=c.PHONE_NUMBER,
            email=c.EMAIL,
            websites=c.WEBSITES
        )

    if "academic_references" not in c.OMIT_SECTIONS:
        body += sc.create_academic_references(c.REFERENCES, c.MAXREF)

    if "research_interests" not in c.OMIT_SECTIONS:
        body += sc.create_research_interests(c.RESEARCH_INTERESTS)

    if "education" not in c.OMIT_SECTIONS:
        body += sc.create_education(c.KEEP_UNDERGRAD, c.KEEP_SECONDARY, c.KEEP_UNDERGRAD_COURSES)

    if "professional_experience" not in c.OMIT_SECTIONS:
        body += sc.create_professional_experience(c.JOBS, c.JOB_MIN_RATING, c.JOB_MIN_DATE)

    if "software" not in c.OMIT_SECTIONS:
        body += sc.create_software(c.MAX_REPOS, c.BLACKLIST)

    if "academic_experience" not in c.OMIT_SECTIONS:
        body += sc.create_academic_experience(
            c.OMIT_GRANTS, c.OMIT_COLLABORATIONS, c.OMIT_COMMITTEES,
            c.OMIT_REFEREES, c.OMIT_LECTURING, c.OMIT_SUPERVISION,
            c.OMIT_TEACHING, c.OMIT_OUTREACH, c.OMIT_PROF_TRAINING,
            c.OMIT_PERSONAL_TRAINING, c.OMIT_INDUSTRY)

    if "awards_and_scholarships" not in c.OMIT_SECTIONS:
        body += sc.create_awards_and_scholarships(c.AWARDS_MIN_YEAR, c.AWARDS_MIN_RATING)

    if "technical_skills" not in c.OMIT_SECTIONS:
        body += sc.create_technical_skills()


    if "press_releases" not in c.OMIT_SECTIONS:
        body += sc.create_press_releases()

    if "presentations" not in c.OMIT_SECTIONS:
        body += sc.create_presentations(c.WRITE_POSTERS, c.WRITE_LOCAL_TALKS)

    if "publications" not in c.OMIT_SECTIONS:
        publist = sc.create_publications(c.LIBRARY, c.SURNAME, c.STUDENTS)

        print("    Writing standalone publication list to outputs/publist.pdf")
        # Write out the publication list standalone
        pubdoc = document.replace(r"{%body%}", publist)
        pubdoc = pubdoc.replace(r"{%doctype%}", "Publication List")

        # write out and compile the publist
        with open("outputs/publist.tex", 'w') as f:
            f.write(pubdoc)

        os.chdir("outputs")
        compile_latex("publist.tex")
        os.chdir("..")
    else:
        publist = ""

    document = document.replace(r"{%doctype%}", "C.V.")

    for kind in ['nopubs', 'full']:
        if kind == "full":
            doc = document.replace(r"{%body%}", body + publist)

        elif kind == "nopubs":
            doc = document.replace(r"{%body%}", body)
        cvname = f"cv_{kind}.tex"

        print(f"""Writing CV with{"out" if kind == 'nopubs' else ""} publist at outputs/{cvname}""")

        # Write out a tex file
        with open(f"outputs/{cvname}", 'w') as f:
            f.write(doc)

        # Compile the Document
        os.chdir("outputs")
        compile_latex(cvname)
        os.chdir("..")
