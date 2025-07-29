
CVE_REGEX = r'CVE-\d{4}-\d{4,7}'

CVSS_V2_PATTERN = (r'^((AV:[NAL]|AC:[LMH]|Au:[MSN]|[CIA]:[NPC]|E:(U|POC|F|H|ND)|RL:(OF|TF|W|U|ND)|RC:(UC|UR|C|ND)|'
                   r'CDP:(N|L|LM|MH|H|ND)|TD:(N|L|M|H|ND)|[CIA]R:(L|M|H|ND))\/)*(AV:[NAL]|AC:[LMH]|Au:[MSN]|'
                   r'[CIA]:[NPC]|E:(U|POC|F|H|ND)|RL:(OF|TF|W|U|ND)|RC:(UC|UR|C|ND)|CDP:(N|L|LM|MH|H|ND)|'
                   r'TD:(N|L|M|H|ND)|[CIA]R:(L|M|H|ND))$')

CVSS_V3_PATTERN = (r'^CVSS:3[.][01]\/((AV:[NALP]|AC:[LH]|PR:[NLH]|UI:[NR]|S:[UC]|[CIA]:[NLH]|E:[XUPFH]|RL:[XOTWU]|'
                   r'RC:[XURC]|[CIA]R:[XLMH]|MAV:[XNALP]|MAC:[XLH]|MPR:[XNLH]|MUI:[XNR]|MS:[XUC]|'
                   r'M[CIA]:[XNLH])\/)*(AV:[NALP]|AC:[LH]|PR:[NLH]|UI:[NR]|S:[UC]|[CIA]:[NLH]|E:[XUPFH]|RL:[XOTWU]|'
                   r'RC:[XURC]|[CIA]R:[XLMH]|MAV:[XNALP]|MAC:[XLH]|MPR:[XNLH]|MUI:[XNR]|MS:[XUC]|M[CIA]:[XNLH])$')

CVSS_V4_PATTERN = (r'^CVSS:4[.]0\/AV:[NALP]\/AC:[LH]\/AT:[NP]\/PR:[NLH]\/UI:[NPA]\/VC:[HLN]\/VI:[HLN]\/VA:[HLN]\/SC:'
                   r'[HLN]\/SI:[HLN]\/SA:[HLN](\/E:[XAPU])?(\/CR:[XHML])?(\/IR:[XHML])?(\/AR:[XHML])?(\/MAV:'
                   r'[XNALP])?(\/MAC:[XLH])?(\/MAT:[XNP])?(\/MPR:[XNLH])?(\/MUI:[XNPA])?(\/MVC:[XNLH])?(\/MVI:'
                   r'[XNLH])?(\/MVA:[XNLH])?(\/MSC:[XNLH])?(\/MSI:[XNLHS])?(\/MSA:[XNLHS])?(\/S:[XNP])?(\/AU:[XNY])?'
                   r'(\/R:[XAUI])?(\/V:[XDC])?(\/RE:[XLMH])?(\/U:(X|Clear|Green|Amber|Red))?$')
