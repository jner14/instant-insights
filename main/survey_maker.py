import plotly.plotly as plty
import plotly.graph_objs as gobj
import pdfkit
from datetime import date
import os


class SuveyReportMaker():
    def __init__(self, survey_data, user_name, rating, api_cred):
        """Creates Innovation Company survey reports PDF files.
		
		Args:
			survey_data (list of list of str): A list containing each entry
				of the survey. 
		
		"""
        self.resp_num = len(survey_data)
        self.survey_data = self.process_survey_data(survey_data)
        self.user_name = user_name
        self.rating = rating

        plty.sign_in(*api_cred)

    @staticmethod
    def process_survey_data(survey_data):
        """Converts survey data responses to readable output; counts instances
		
		Args:
			survey_data (list of list of str): A list containing each entry
				of the survey. First element of the list is the type of
				respondent (either an associate or manager), second element is
				the answers from 'a' for High, to 'd' for No, in terms of 
				perceived risk, and third element is the answers for the 
				respondent in terms of perceived failure.
		
		Returns:
			(dict of str => 
				dict of str => 
					dict of str => int): A dictonary is produced with two
				keys, one for associates and one for managers. The 
				sub-dictonary contains keys for 'Risk' and for 'Failure',
				in which the totals for each category are kept.
		"""
        datamap = {
            'Risk': {
                'a': 'High',
                'b': 'Medium',
                'c': 'Low',
                'd': 'No',
            },
            'Failure': {
                'a': 'Supported',
                'b': 'Injured',
                'c': 'Booted',
            },
        }
        results = {
            'Managers': {'Risk': {k: 0 for k in datamap['Risk'].values()},
                         'Failure': {k: 0 for k in datamap['Failure'].values()}},
            'Associates': {'Risk': {k: 0 for k in datamap['Risk'].values()},
                           'Failure': {k: 0 for k in datamap['Failure'].values()}},
        }
        for entry in survey_data:
            current_key = None
            if entry[0] == 'ASSOC':
                current_key = 'Associates'
            else:
                current_key = 'Managers'
            risk_val = datamap['Risk'][entry[1]]
            fail_val = datamap['Failure'][entry[2]]
            results[current_key]['Risk'][risk_val] += 1
            results[current_key]['Failure'][fail_val] += 1
        return results

    def return_overall(self, vals):
        overall = vals[0]
        for typ in vals[0].keys():
            overall[typ] = {
                k: overall[typ][k] + vals[1][typ][k] for k in vals[1][typ]
                }
        return overall

    def _make_plot(self, data, title, fname):
        layout = None
        if len(data) > 1:
            layout = gobj.Layout(barmode='group', title=title,
                                 width=400, height=320)
        else:
            layout = gobj.Layout(title=title, width=400, height=320)
        fig = gobj.Figure(data=data, layout=layout)

        plty.image.save_as(fig, filename=fname)

    def make_plots(self):
        overall = self.return_overall(self.survey_data.values())
        typs = overall.keys()

        for typ in typs:
            overall_data = [gobj.Bar(
                x=[k for k in overall[typ].keys()],
                y=[v for v in overall[typ].values()]
            )]
            man_data = gobj.Bar(
                x=[k for k in self.survey_data['Managers'][typ].keys()],
                y=[v for v in self.survey_data['Managers'][typ].values()],
                name="Managers"
            )
            assoc_data = gobj.Bar(
                x=[k for k in self.survey_data['Associates'][typ].keys()],
                y=[v for v in self.survey_data['Associates'][typ].values()],
                name="Associates"
            )
            title = "Level of RISK" if typ == 'Risk' \
                else "Perception of FAILURE"
            self._make_plot(overall_data, title, "Overall_" + typ + ".png")
            self._make_plot([man_data, assoc_data], title, "Grouped_" + typ + ".png")

    def write_to_pdf(self, pg, ofname="out.pdf", config=None):
        if config:
            pdfkit.from_string(pg, ofname, configuration=config)
        else:
            pdfkit.from_string(pg, ofname)

    def make_html_page(self):
        return """<html>
<head>
</head>
<body>
<style type="text/css">
#wrap {
   width:600px;
   margin:0 auto;
}
#left_col {
   float:left;
   width:300px;
}
#right_col {
   float:right;
   width:300px;
}
</style>
<img src=""" + os.path.join(os.getcwd(), "innovation_company_logo.png") + """ />
<p>Thank you for using The Innovation Company's I3&trade; Assessment Tool.  Below are your results.</p>
<div id="wrap">
	<div id="left_col">
		<p>Date of this report: """ + date.today().strftime("%m/%d/%Y") + """</br>
		Your name: """ + self.user_name + """</br>
		Number of respondents: """ + str(self.resp_num) + """</p>
		
	</div>
	<div id="right_col">
		<h2>WARM to COLD</h2>
		<p>""" + str(self.rating) + """</p>
	</div>
</div>
<table>
	<tr>
		<td><img src=""" + os.path.join(os.getcwd(), "Overall_Risk.png") + """ /></td>
		<td><img src=""" + os.path.join(os.getcwd(), "Overall_Failure.png") + """ /></td>
	</tr>
	<tr>
		<td><img src=""" + os.path.join(os.getcwd(), "Grouped_Risk.png") + """ /></td>
		<td><img src=""" + os.path.join(os.getcwd(), "Grouped_Failure.png") + """ /></td>
	</tr>
</table>
<p>*Responses were entered into The Innovation Company's proprietary I3 scoring algorithm and your result is based on a HOT - WARM - COLD scale where HOT is best.</p>
<p><strong>Next steps:</strong> Please contact us at 978-266-0012 or <a href="info@innovationisEASY.com">info@innovationisEASY.com</a> to schedule a time discuss these results and explore specific action items via 1 hour of FREE consultation.  If you would like to start some work on your own please checkout our FREE apps, games, and Innovation DIY process at <a href="http://www.innovationiseasy.com/diy.html">http://www.innovationiseasy.com/diy.html</a></p>
<div style="text-align: center;">
	<h3>Thank you for using our I3&trade; Assessment Tool!</h3>
	<p style="color: grey;">Copywright 2017 The Innovation Company, LLC All rights reserved</p>
	<p style="color: grey;">website: <a href="http://www.innovationiseasy.com/diy.html">www.inovationisEASY.com</a></p>
	<p style="color: grey;">email: <a href="info@innovationisEASY.com">info@innovationisEASY.com</a></p>
</div>
</body>
</html>
		"""


if __name__ == '__main__':
    import csv

    with open("Company 1.csv", 'rb') as cpin:
        cpin_reader = csv.reader(cpin, delimiter=',')
        cpin_reader.next()
        sdata = [line for line in cpin_reader]
        # NEED THIS => (plotly.user_name, plotly.api_key
        api_cred = ("innovationiseasy", "ZHBgmFenRod0v8WvH4OE")
        srmaker = SuveyReportMaker(sdata, "Crimson Star Software", 9001, api_cred)
        srmaker.make_plots()
        pg = srmaker.make_html_page()
        config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
        srmaker.write_to_pdf(pg, config=config)
