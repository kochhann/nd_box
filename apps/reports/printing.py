from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.contrib.auth.models import User
from reportlab.pdfgen import canvas
from reportlab.platypus.flowables import PageBreak, Spacer
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.platypus.frames import Frame
from reportlab.lib.units import inch, cm, mm


# from views import  namedtuplefetchall

class MyPrint:

    ## Construtor
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        elif pagesize == 'Letter':
            self.pagesize = A4
        self.width, self.height = self.pagesize

    ## Gerador de Cabecalho e rodape
    def _header_footer(request, canvas, doc):
        # Save the state of our canvas so we can draw on it
        canvas.saveState()
        styles = getSampleStyleSheet()

        # Header
        header = Paragraph('This is a multi-line header.  It goes on every page.   ' * 5, styles['Normal'])
        # I = Image('C:/Users/Juliano/pythonProject/liraHML/locacao/static/images/logos/docHeader.jpg')
        # I.drawHeight = 2 * cm
        # I.drawWidth = 19 * cm
        # header = I
        #        header.append(I)
        #        header.append(Spacer(1,0.4*cm))
        w, h = header.wrap(doc.width, doc.topMargin)
        # header.drawOn(canvas, doc.leftMargin, 27 * cm)

        f1 = ParagraphStyle(
            name='footer1',
            fontName='Times-Roman',
            alignment=TA_CENTER,
            fontSize=12,
            leading=14)

        # Footer
        footer = Paragraph("Texto do rodapé", f1)
        w, h = footer.wrap(doc.width, doc.bottomMargin)
        footer.drawOn(canvas, doc.leftMargin, 0.4 * cm)

        # Release the canvas
        canvas.restoreState()

    def print_users(self):
        buffer = self.buffer
        doc = SimpleDocTemplate(buffer, topMargin=3 * cm, rightMargin=30, leftMargin=30,
                                bottomMargin=2)  # ,pagesize=self.pagesize)

        # Our container for 'Flowable' objects
        elements = []

        # A large collection of style sheets pre-made for us
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='centered', alignment=TA_CENTER))

        # Draw things on the PDF. Here's where the PDF generation happens.
        # See the ReportLab documentation for the full list of functionality.
        users = User.objects.all()
        elements.append(Spacer(1, 5 * cm))
        elements.append(Paragraph('My User Names', styles['Heading1']))
        for i, user in enumerate(users):
            elements.append(Paragraph(user.get_full_name(), styles['Normal']))
        elements.append(Paragraph('USER     ' * 1000, styles['Heading1']))

        doc.build(elements, onFirstPage=self._header_footer, onLaterPages=self._header_footer,
                  canvasmaker=NumberedCanvas)

        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()
        return pdf


## Classe responsavel por numerar as paginas
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        # Change the font type and size of this to whatever you want the page number to be
        canvas.Canvas.setFont(self, 'Times-Roman', 10)
        # Change the position of this to wherever you want the page number to be
        self.drawRightString(105 * mm, 12 * mm + (0.2 * inch),
                             "%d" % self._pageNumber)
