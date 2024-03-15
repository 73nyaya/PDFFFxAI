import pdfrw
import data_model_440
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A3
from typing import List,Dict, Optional
from pydantic import BaseModel, ValidationError
import pandas as pd
from pathlib import Path

data_folder = Path.cwd() / 'J440 - BHP Handrails Inspection'

fields = [
    'Submission Id',
    'Damage Mechanism',
    'Type',
    'Condition',
    'Facility',
    'Area',
    'Asset code',
    'Component',
    'Defect Location Description',
    'Date',
    'Defect Detailed Description',
    'Component Final Failure Mode',
    'Component Final Failure Mode (Not listed)',
    'Effect to the Equipment due to Component Failure',
    'Impact as per NIW-ENG-STD-0010 AIMS V1.0',
    'Severity Level',
    'Consequence',
    'Reason for Consequence Selection',
    'Reason for Consequence Selection (Not listed)',
    'Likelihood',
    'Defect priorisation',
    'Required action',
    'Isolation Required?',
    'Monitor?',
    'Equipment Constraints',
    'Type of Work to be Completed',
    'Corrective Action',
    'Corrective Action Summary (Not listed)',
    'Access Requirements',
    'Permits Required',
    'Repair Quality Verification Level',
    'Work Requirements',
    'Photo 1',
    'Photo 2',
    'Photo 3',
    'Photo 4',
    'Photo 5',
    'Photo 6',
    ]

def launch(**data: dict) -> dict:
        damage = dict(damage_mech=data["Damage Mechanism"],
                        type=data["Type"],
                        condition=data["Condition"])
        location= dict(facility=data["Facility"],
                            area=data["Area"],
                            asset=data['Asset code'],
                            component=data["Component"],
                            location=data["Defect Location Description"],
                            date=data['Date'])
        risk_assessment = dict(detailed_description=data['Defect Detailed Description'],
                               final_failure_mode=data['Component Final Failure Mode'],
                               final_failure_mode_add=data['Component Final Failure Mode (Not listed)'],
                               effect=data['Effect to the Equipment due to Component Failure'])
        impact = dict(impact=data['Impact as per NIW-ENG-STD-0010 AIMS V1.0'],
                        severity=data['Severity Level'],
                        consequence=data['Consequence'],
                        reason=data['Reason for Consequence Selection'],
                        reason_add=data['Reason for Consequence Selection (Not listed)'],
                        likelihood=data['Likelihood'],
                        priority=data['Defect priorisation'])
        methodology = dict(required_action=data['Required action'],
                                  isolation=data['Isolation Required?'],
                                  monitor=data['Monitor?'],
                                  constraints=data['Equipment Constraints'],
                                  type_of_work=data['Type of Work to be Completed'],
                                  access=data['Access Requirements'],
                                  permits=data['Permits Required'],
                                  verification=data['Repair Quality Verification Level'],
                                  work_requirements=data['Work Requirements'],
                                  corrective_action=data['Corrective Action'],
                                  corrective_action_add=data['Corrective Action Summary (Not listed)'])
        return dict(damage=damage, 
                    location = location, 
                    risk_assessment=risk_assessment,
                    impact = impact,
                    methodology= methodology)
        
def build_photo_path(row: pd.Series, i: int) -> Optional[str]:
    '''Replaces the Photo columns of the DF with the actual path of the photos. To be stored in ./J440 - BHP Handrails Inspection'''
    if isinstance(row[f"Photo {i}"], str):
        photo_path = str(data_folder / ", {area}, {component}_{sub_id}".format(area=row["Area"], component=row["Component"], sub_id=row["Submission Id"]) / str(row[f"Photo {i}"]))
        return photo_path
    
def  process_data(df: pd.DataFrame, defaults: Dict) -> pd.DataFrame:
    '''Preprocess the data and validates to catch validation errors. If all is ok return a dataframe ready for data printing.'''
    for i in range(1,7):
        df[f"Photo {i}"] = df[["Submission Id", "Area", "Component", f"Photo {i}"]].apply(lambda row: build_photo_path(row, i), axis=1)
    for column in defaults.keys():
        df[column]=defaults[column]
    df.fillna('', inplace=True)
    return df[fields]

def create_overlay_pdf(image_paths:List, overlay_pdf_path:str, top_left_x:float,
                       top_left_y:float, width:float, height:float, spacing:float)->None :
    """
    Create a PDF with multiple images with specified spacing between them. 
    PDF name is overlay.PDF.
    """
    # Calculate positions for all images based on the first image's position and spacing
    positions = [{
        'top_left_x': top_left_x + i * (width + spacing),
        'top_left_y': top_left_y,
        'width': width,
        'height': height
    } for i in range(len(image_paths))]
    
    # Create a new PDF with the images
    c = canvas.Canvas(overlay_pdf_path, pagesize=landscape(A3))
    for image_path, position in zip(image_paths, positions):
        c.drawImage(image_path, position['top_left_x'], position['top_left_y'], width=position['width'], height=position['height'])
    c.save()


def fill_fields(fields:Dict,filled_output_dir:str,template:str='J440_Templates/P1.pdf')-> any:
    """ fill all texbox in the template. It returns a pdfrw object """
    input_pdf = pdfrw.PdfReader(template)

    input_pdf.Root.AcroForm.update(pdfrw.PdfDict(NeedAppearances=pdfrw.PdfObject('true')))
    for x in range(0, len(input_pdf.Root.AcroForm.Fields)):
        key  = input_pdf.Root.AcroForm.Fields[x].T[1:-1]
        if  key in fields.keys():
            input_pdf.Root.AcroForm.Fields[x].update(pdfrw.PdfDict(V= fields[key]))

            # this section doesnt fit with arial 12 thus I reduce it to 11
            if key == 'DAMAGE2':
                font_size = pdfrw.objects.pdfstring.PdfString.encode('0 g /Arial 11 Tf')
                input_pdf.Root.AcroForm.Fields[x].update({'/DA': font_size})

            if key == 'Risk_Ranking':
                print('rating' , fields[key])
    writer = pdfrw.PdfWriter()
    writer.write(filled_output_dir, input_pdf)
    return input_pdf

def concat_pdfs(pdf1:str, pdf2:str, output:str)->None:
    """ 
    Reads the filled pdf (form) and reads the overlay images (Olay) and merges the files.
    "output" is the names of resulting PDF
    """
    form = pdfrw.PdfReader(pdf1)
    olay = pdfrw.PdfReader(pdf2)
    
    for form_page, overlay_page in zip(form.pages, olay.pages):
        merge_obj = pdfrw.PageMerge()
        overlay = merge_obj.add(overlay_page)[0]
        pdfrw.PageMerge(form_page).add(overlay).render()
        
    writer = pdfrw.PdfWriter()
    writer.write(output, form)

def main(fields:Dict,overlay_dir:str,template_dir:str,filled_output_dir:str,
         merge_dir:str,image_paths:List,top_left_x:float,top_left_y:float,
         width:float, height:float, spacing:float)->None:
    
    # create image overlay 
    create_overlay_pdf(image_paths, overlay_dir, top_left_x,
                       top_left_y, width, height, spacing)
    # fill pdf form 
    fill_fields(fields,filled_output_dir,template_dir)

    # merge pdf 
    concat_pdfs(filled_output_dir,overlay_dir,merge_dir)


df = pd.read_excel(data_folder / 'f7aa715f-0a5e-4886-9f76-6b63e94a91c2.xlsx', sheet_name="Root")

defaults = dict(Facility = "BHP Nickel West", Date="")

records = process_data(df=df, defaults=defaults)
records.to_excel('filename.xlsx', sheet_name='Sheet1', index=False)
records = records.to_dict(orient='records')
top_left_x = 200  
top_left_y = 50  
width = 275     
height = 300     
spacing = 50 
validated_reports = []
for record in records:
    print(record)

    try:
        # Create an instance of the BaseModel with the record data
        report_data = data_model_440.InspectionReport(**launch(**record))
        # Append the instance to the list of validated users
        validated_reports.append(report_data)
        image_paths = [record["Photo 1"], record["Photo 2"], record["Photo 3"]]
        filled_output_dir = 'filled_pdf.pdf'
        overlay_dir = 'overlay.pdf'
        merge_dir = f'Output/{record['Submission Id']}.pdf'
        template_dir =r"J440_Templates/P1.pdf"
        main(report_data.to_custom_dict(),overlay_dir,template_dir,filled_output_dir,
            merge_dir,image_paths,top_left_x,top_left_y,width,
            height,spacing)

    except ValidationError as e:
        # Handle the validation error as needed (e.g., log it, skip, etc.)
        print(f"Validation error for record {record['Submission Id']}: {e}")
    
print(len(validated_reports))




exit()
if __name__ == '__main__':

    #  Export pydantic model in Dict
    fields = PDF_dict2
    # image list
    image_paths = [
    r'images\IMG_3369_20240222121404.JPG',
    r'images\IMG_3370_20240222121408.JPG',
    r'images\IMG_3371_20240222121413.JPG',
    ]
    # image settings
    top_left_x = 200  
    top_left_y = 50  
    width = 250      
    height = 300     
    spacing = 50   
    
    # filled pdf name
    filled_output_dir = 'filled_pdf.pdf'
    overlay_dir = 'overlay.pdf'
    merge_dir = 'report_example.pdf'
    template_dir =r"Templates\moderate_template.pdf"
    main(fields,overlay_dir,template_dir,filled_output_dir,
        merge_dir,image_paths,top_left_x,top_left_y,width,
        height,spacing)