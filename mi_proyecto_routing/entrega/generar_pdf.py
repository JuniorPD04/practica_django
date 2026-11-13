"""Genera la entrega con presentación IEEE adaptada a interlineado 1.5."""
import argparse
import json
import re
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, Image, KeepTogether, NextPageTemplate,
    PageBreak, PageTemplate, Paragraph, Spacer,
)


def fonts():
    """Usa Times New Roman cuando está instalado; Times es el respaldo portable."""
    directory = Path('C:/Windows/Fonts')
    if all((directory / name).exists() for name in ('times.ttf', 'timesbd.ttf', 'timesi.ttf')):
        for name, filename in [('TNR', 'times.ttf'), ('TNR-Bold', 'timesbd.ttf'), ('TNR-Italic', 'timesi.ttf')]:
            pdfmetrics.registerFont(TTFont(name, str(directory / filename)))
        return 'TNR', 'TNR-Bold', 'TNR-Italic'
    return 'Times-Roman', 'Times-Bold', 'Times-Italic'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='https://routing-api-kde6.onrender.com')
    parser.add_argument('--imagen', type=Path, help='Captura original de /authors; por defecto imagen_autores.png')
    args = parser.parse_args()
    if not re.fullmatch(r'https://[A-Za-z0-9.-]+/?', args.url):
        parser.error('Usa la URL base HTTPS sin rutas, parámetros ni credenciales.')
    folder = Path(__file__).resolve().parent
    image_path = args.imagen or folder / 'imagen_autores.png'
    if not image_path.is_file():
        parser.error(f'No se encontró la captura original: {image_path}')
    authors = json.loads((folder.parent / 'authors.json').read_text(encoding='utf-8'))
    output = folder / 'Perez_Junior_Despliegue.pdf'
    regular, bold, italic = fonts()

    def style(name, size=10, align=TA_JUSTIFY, font=None, **kwargs):
        return ParagraphStyle(name, fontName=font or regular, fontSize=size,
                              leading=size * 1.5, alignment=align, textColor=colors.black,
                              **kwargs)

    body = style('Respuesta', firstLineIndent=0.35*cm, spaceAfter=8)
    question = style('Pregunta', align=TA_LEFT, font=bold, spaceBefore=7,
                     spaceAfter=4, keepWithNext=True)
    section = style('Sección', size=11, align=TA_CENTER, spaceAfter=10, keepWithNext=True)
    cover_title = style('Título', size=18, align=TA_CENTER, font=bold, spaceAfter=16)
    cover = style('Portada', size=12, align=TA_CENTER, spaceAfter=9)
    caption = style('Figura', size=10, align=TA_CENTER, spaceBefore=7, spaceAfter=12)
    evidence_body = style('Evidencia', size=11, firstLineIndent=0.5*cm, spaceAfter=14)
    url = args.url.rstrip('/')
    story = [Spacer(1, 2*cm), Paragraph('DESARROLLO WEB', cover_title),
             Paragraph('Despliegue de backend con Django', cover_title),
             Paragraph('Python, PostgreSQL y Render', cover), Spacer(1, 1*cm)]
    for author in authors:
        story.append(Paragraph(escape(f"{author['nombre']} - {author['codigo']}"), cover))
    story += [Spacer(1, 0.9*cm), Paragraph('Proyecto: mi_proyecto_routing', cover),
              Paragraph('Repositorio: https://github.com/JuniorPD04/practica_django', cover),
              Paragraph(f'Servicio: {escape(url)}', cover),
              Paragraph(f'Verificación: {escape(url)}/authors', cover),
              Spacer(1, 0.7*cm), Paragraph('13 de noviembre de 2026', cover),
              NextPageTemplate('cuestionario'), PageBreak(),
              Paragraph('I. CUESTIONARIO', section)]

    text = (folder / 'CUESTIONARIO.md').read_text(encoding='utf-8')
    text = text.replace('\u2014', '-').replace('\u2013', '-')
    for block in text.strip().split('\n\n'):
        if block.startswith('# '):
            continue
        if block.startswith('## '):
            story.append(Paragraph(escape(block[3:]), question))
        else:
            story.append(Paragraph(escape(block.replace('\n', ' ')), body))

    story += [NextPageTemplate('evidencia'), PageBreak(),
              Paragraph('II. EVIDENCIA DEL DESPLIEGUE', section),
              Paragraph('La siguiente captura muestra la consulta a /authors desde el navegador. '
                        'La respuesta presenta los nombres y códigos de los tres integrantes, '
                        'sin que sea necesario iniciar sesión ni enviar un token de autenticación.', evidence_body)]
    image = Image(str(image_path))
    width = A4[0] - 4*cm
    image.drawHeight = image.imageHeight * width / image.imageWidth
    image.drawWidth = width
    story.append(KeepTogether([
        image,
        Paragraph('Fig. 1. Respuesta pública de /authors sin credenciales.', caption),
    ]))
    story.append(Paragraph(f'Dirección consultada: {escape(url)}/authors.', evidence_body))

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(colors.black)
        canvas.setFont(regular, 9)
        canvas.drawCentredString(A4[0]/2, 1.1*cm, str(doc.page))
        canvas.restoreState()

    margin = 2*cm
    height = A4[1] - 4*cm
    def frame(name, x, frame_width):
        return Frame(x, margin, frame_width, height, id=name,
                     leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)

    doc = BaseDocTemplate(str(output), pagesize=A4,
                          title='Despliegue de backend con Django',
                          author=', '.join(a['nombre'] for a in authors))
    doc.addPageTemplates([
        PageTemplate(id='portada', frames=[frame('portada', margin, width)], onPage=footer),
        PageTemplate(id='cuestionario', frames=[frame('cuestionario', margin, width)], onPage=footer),
        PageTemplate(id='evidencia', frames=[frame('evidencia', margin, width)], onPage=footer),
    ])
    doc.build(story)
    print(f'PDF generado: {output}')
    print('Times; texto negro; respuestas justificadas; interlineado 1.5; captura original incluida.')


if __name__ == '__main__':
    main()
