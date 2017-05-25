#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Module for generating Innovation Company reports as PDF files
    
File name: survey_maker.py
Author: Thomas Adriaan Hellinger
Date created: 5/15/2017
Date last modified: 5/17/2017
Python Version: 2.7

Copywright 2017 The Innovation Company, LLC All rights reserved    
"""
from datetime import date
import os
import tempfile

import pdfkit
import plotly.plotly as plty
import plotly.graph_objs as gobj

import conf


class SurveyReportMaker():
    def __init__(self, survey_data, user_name, rating, api_cred=None):
        """Creates Innovation Company survey reports PDF files.
        
        Args:
            survey_data (list of list of str): A list containing each entry
                of the survey. 
            user_name (str): Name of the company requesting the report.
            rating (str): 
            api_cred (2-tuple, str, optional): A 2-tuple containing a Plotly
                username, and API key; in that order. If not provided, the
                SurveyReportMaker instance will not log onto Plotly. Note:
                logging into Plotly is necessary to ultimately print the
                report.
        """
        self.resp_num = len(survey_data)
        self.survey_data = self.process_survey_data(survey_data)
        self.user_name = user_name
        self.rating = rating

        if api_cred:
            self.plotly_login(api_cred)
        else:
            self.isLoggedIntoPlotly = False

    def plotly_login(self, api_cred):
        """Used to login to Plot.ly graphing API
        
            api_cred (2-tuple, str, optional): A 2-tuple containing a Plotly
                username, and API key; in that order. If not provided, the
                SurveyReportMaker instance will not log onto Plotly. Note:
                logging into Plotly is necessary to ultimately print the
                report.
        """
        plty.sign_in(*api_cred)
        self.isLoggedIntoPlotly = True

    def process_survey_data(self, survey_data):
        """Converts survey data responses to readable output; counts instances
        
        Note: a side effect of this function is to create `self.resp_man` (ie.
            number of managers) and `self.resp_asc` (ie. number of associates)
        
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
                    dict of str => int): A dictionary is produced with two
                keys, one for associates and one for managers. The 
                sub-dictionary contains keys for 'Risk' and for 'Failure',
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
        self.resp_asc = 0
        self.resp_man = 0
        for entry in survey_data:
            current_key = None
            if entry[0] == 'ASSOC':
                current_key = 'Associates'
                self.resp_asc += 1
            else:
                current_key = 'Managers'
                self.resp_man += 1
            risk_val = datamap['Risk'][entry[1]]
            fail_val = datamap['Failure'][entry[2]]
            results[current_key]['Risk'][risk_val] += 1
            results[current_key]['Failure'][fail_val] += 1
        return results

    def return_overall(self, vals):
        """Combines the counts of associates and managers
        
        Adds together the counts of associates and managers, in terms of risk
        and failure.
        
        Args:
            vals (list of dict of str => 
                    dict of str => int): Expects a list of two dictonaries.
                See the `results` variable of the method:
                ~SurveyReportMaker.process_survey_data.
        
        Returns:
            (dict of str => 
                dict of str => int): This is the combination of the
            "Risk" and "Failure" counts of managers and associates.
        """
        overall = vals[0].copy()
        for typ in vals[0].keys():
            overall[typ] = {
                k: overall[typ][k] + vals[1][typ][k] for k in vals[1][typ]
                }
        return overall

    def _make_plot(self, data, fname, title=None):
        layout = None
        annotations = None
        if len(data) > 1:
            manCount = float(sum(data[0].y))
            assCount = float(sum(data[1].y))
            ann = [j for i in zip([
                                      dict(
                                          x=xi,
                                          y=yi,
                                          text="0%" if manCount == 0 else "{0:.0f}".format(100 * float(yi) / manCount) + "%",
                                          xanchor='right',
                                          yanchor='bottom',
                                          showarrow=False,
                                      ) for xi, yi in zip(data[0].x, data[0].y)],
                                  [dict(
                                      x=xi,
                                      y=yi,
                                      text="0%" if assCount == 0 else "{0:.0f}".format(100 * float(yi) / assCount) + "%",
                                      xanchor='left',
                                      yanchor='bottom',
                                      showarrow=False,
                                  ) for xi, yi in zip(data[1].x, data[1].y)]
                                  ) for j in i]
            layout = gobj.Layout(barmode='group',
                                 title=title,
                                 legend=dict(orientation="h"),
                                 margin=gobj.Margin(l=50, r=50, b=10, t=10, pad=2),
                                 annotations=ann,
                                 width=300,
                                 height=240,
                                 yaxis=dict(
                                     autorange=True,
                                     showgrid=False,
                                     zeroline=False,
                                     showline=False,
                                     autotick=True,
                                     ticks='',
                                     showticklabels=False
                                 ))
        else:
            ann = [
                dict(
                    x=xi,
                    y=yi,
                    text=str(yi),
                    xanchor='right',
                    yanchor='bottom',
                    showarrow=False,
                ) for xi, yi in zip(data[0].x, data[0].y)
                ]
            layout = gobj.Layout(title=title,
                                 annotations=ann,
                                 legend=dict(orientation="h"),
                                 margin=gobj.Margin(l=50, r=50, b=25, t=25, pad=2),
                                 width=300,
                                 height=240,
                                 yaxis=dict(
                                     autorange=True,
                                     showgrid=False,
                                     zeroline=False,
                                     showline=False,
                                     autotick=True,
                                     ticks='',
                                     showticklabels=False
                                 ))
        fig = gobj.Figure(data=data, layout=layout)
        setattr(self, fname, tempfile.NamedTemporaryFile(mode='wb', suffix='.png'))
        # Close file if on windows otherwise access denied error
        if __name__ == "__main__":
            getattr(self, fname).close()
        plty.image.save_as(fig, filename=getattr(self, fname).name)

    def make_plots(self):
        """Accesses the Plot.ly API to make the bar charts for the report.

        Creates temporary files to download charts from Plot.ly API.
        """
        overall = self.return_overall(self.survey_data.values())
        typs = overall.keys()

        for typ in typs:
            if typ == 'Failure':
                keys = ['Supported', 'Injured', 'Booted']
            else:
                keys = ['High', 'Medium', 'Low', 'No']

            overall_data = [gobj.Bar(
                marker=dict(color='rgb(165, 209, 121)'),
                x=keys,
                y=[overall[typ][k] for k in keys],
                width=.5
            )]
            man_data = gobj.Bar(
                marker=dict(color='rgb(103, 149, 235)'),
                x=keys,
                y=[self.survey_data['Managers'][typ][k] for k in keys],
                name="Managers",
                width=.5
            )
            assoc_data = gobj.Bar(
                marker=dict(color='rgb(198, 105, 105)'),
                x=keys,
                y=[self.survey_data['Associates'][typ][k] for k in keys],
                name="Associates",
                width=.5
            )
            self._make_plot(overall_data, "overall_" + typ.lower())
            self._make_plot([man_data, assoc_data], "grouped_" + typ.lower())

    def write_to_pdf(self, html, config, ofname=""):
        """Uses pdfkit to write a PDF file based on HTML string input.

        Closes all the 
        
        Args:
            html (str): HTML input string, representing Innovation Company
                report.
            ofname (str): Output file name.
            config (~pdfkit.configuration): pdfkit configuration object,
                may be necessary to point to the `wkhtmltopdf` executable.
        """
        pdf = None
        try:
            if ofname == "":
                pdf = pdfkit.from_string(html, False, configuration=config)
                # pdfkit.from_string(html, ofname, configuration=config)
            else:
                pdfkit.from_string(html, ofname, configuration=config)
                # pdfkit.from_string(html, ofname)
        finally:
            self.grouped_failure.close()
            self.grouped_risk.close()
            self.overall_failure.close()
            self.overall_risk.close()
            return pdf

    def make_html_page(self, logopath):
        """Creates an HTML markup of Innovation Company report
        
        Deletes the temporary files created in ~SurveyReportMaker.make_plots
        method.
        
        Args:
            logopath (str): The path to the Innovation Company logo file.
        
        Returns:
            (str): A HTML markup of the Innovation Company report which can
                be converted to a PDF file.
        """
        self.user_name = self.user_name if self.user_name else ""
        self.resp_num = str(self.resp_num)
        self.resp_asc = str(self.resp_asc)
        self.resp_man = str(self.resp_man)
        self.rating = self.rating if self.rating else ""
        return """<html>
<head>
</head>
<body style="font-family: Calibri, Helvetica, Arial, sans-serif; font-size: 20px;">
<style type="text/css">
#wrap {
   margin:0 auto;
}
#left_col {
   float:left;
   text-align: left;
}
#right_col {
   float:right;
   text-align: center;
   margin-right: 5em;
}
.noBorder {
    border: 0px;
    padding:0; 
    margin:0;
    border-collapse: collapse;
}
.tdw {
    width: 45%;
    padding-bottom: 5px;
    padding-right: 5px;
}
.tdl {
    width: 10%;
}
.tdcenter {
    text-align: center;
}
.vertical_dotted_line
{
    padding:0; 
    margin:0;
    border-collapse: collapse;
    border-left: 1px solid lightgray;
    height: 50px;
} 
</style>
<img src=""" + logopath + """ />
<h3>Thank you for using The Innovation Company's I3&trade; Assessment Tool.  Below are your results.</h3>
<div id="wrap">
    <div id="left_col">
        <p>Date of this report: """ + date.today().strftime("%m/%d/%Y") + """</br>
        Your name: """ + self.user_name + """</br>
        Number of respondents: """ + self.resp_num + """</br>
        Number of managers: """ + self.resp_man + """</br>
        Number of associates: """ + self.resp_asc + """</p>
    </div>
    <div id="right_col">
        <p>Your I3 rating*</p>    
        <h2>""" + self.rating + """</h2>
    </div>
</div>
<table>
    <tr>
        <td class="tdl"></td>
        <td class="tdw tdcenter" style="vertical-align: bottom; font-size: 26px;">Level of <strong>RISK</strong></td>
        <td class="tdcenter vertical_dotted_line"></td>
        <td class="tdw tdcenter" style="vertical-align: bottom; font-size: 26px;">Perception of <strong>FAILURE</strong></td>
    </tr>
    <tr>
        <td class="tdl">Overall</td>
        <td class="tdw tdcenter"><img src=""" + os.path.abspath(self.overall_risk.name) + """ border=1 style="border-color: #D3D3D3" /></td>
        <td class="tdcenter vertical_dotted_line"></td>
        <td class="tdw tdcenter"><img src=""" + os.path.abspath(self.overall_failure.name) + """ border=1 style="border-color: #D3D3D3" /></td>
    </tr>
    <tr>
        <td class="tdl">By manager and associate</td>
        <td class="tdw tdcenter"><img src=""" + os.path.abspath(self.grouped_risk.name) + """ border=1 style="border-color: #D3D3D3" /></td>
        <td class="tdcenter vertical_dotted_line"></td>
        <td class="tdw tdcenter"><img src=""" + os.path.abspath(self.grouped_failure.name) + """ border=1 style="border-color: #D3D3D3" /></td>
    </tr>
</table>
<p>
    *Responses were entered into The Innovation Company's proprietary I3 scoring algorithm and your result is based on a
    HOT - WARM - COLD scale where HOT is best.
</p>
<p><strong>Next steps:</strong> Please contact us at 978-266-0012 or <a href="mailto:info@innovationisEASY.com">info@innovationisEASY.com</a> to schedule a time discuss these results and explore specific action items via 1 hour of FREE consultation.  If you would like to start some work on your own please checkout our FREE apps, games, and Innovation DIY process at <a href="http://www.innovationiseasy.com/diy.html">http://www.innovationiseasy.com/diy.html</a></p>
<footer>
    <div style="text-align: center;">
        <h3>Thank you for using our I3&trade; Assessment Tool</h3>
        <p style="color: grey;">Copywright 2017 The Innovation Company, LLC All rights reserved.</p>
        <div class="wrap" style="text-align: center;">
                <p style="color: grey;">
                    <span style="padding-right:5px">www.innovationisEASY.com</span><span>info@innovationisEASY.com</span>
                </p>
        </div>
    </div>
</footer>
</body>
</html>
        """


if __name__ == '__main__':
    import csv

    with open("Company 1.csv", 'rb') as cpin:
        cPinReader = csv.reader(cpin, delimiter=',')
        cPinReader.next()
        sData = [line for line in cPinReader]
        sData = [['MGR', 'a', 'a'], ['MGR', 'b', 'b'], ['ASSOC', 'c', 'c'], ]
        apiCred = ('innovationiseasy', 'ZHBgmFenRod0v8WvH4OE')
        srMaker = SurveyReportMaker(sData, "Crimson Star Software", "WARM TO COLD", apiCred)
        srMaker.make_plots()
        pg = srMaker.make_html_page(os.path.join(os.getcwd(), "innovation_company_logo.png"))
        config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
        srMaker.write_to_pdf(pg, config=config, ofname="testReport.pdf")
        # pdfkit.from_string("Hello World", "testReport.pdf", configuration=config)

        print("Finished")
