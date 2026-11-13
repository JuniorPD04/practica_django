"""Genera el PDF de entrega. Uso: python generar_pdf.py --url https://servicio.onrender.com"""
import argparse
import json
import re
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='', help='URL real del Web Service desplegado')
    args = parser.parse_args()
    if args.url and not re.fullmatch(r'https://[A-Za-z0-9.-]+/?', args.url):
        parser.error('Usa la URL base HTTPS sin rutas, parámetros ni credenciales.')
    folder = Path(__file__).resolve().parent
    authors = json.loads((folder.parent / 'authors.json').read_text(encoding='utf-8'))
    output = folder / 'Perez_Junior_Despliegue.pdf'
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Cover', fontSize=25, leading=31, alignment=TA_CENTER,
                              textColor=colors.HexColor('#193b59'), spaceAfter=25))
    styles.add(ParagraphStyle(name='CoverText', fontSize=12, leading=19, alignment=TA_CENTER,
                              spaceAfter=10))
    styles['BodyText'].fontSize = 10.5
    styles['BodyText'].leading = 15
    styles['BodyText'].spaceAfter = 12
    styles['Heading2'].fontSize = 12
    styles['Heading2'].leading = 16
    url = args.url.rstrip('/')
    story = [Spacer(1, 2*cm), Paragraph('Desarrollo Web<br/>Despliegue de Backend', styles['Cover']),
             Paragraph('Django · Python · PostgreSQL · Render', styles['CoverText']), Spacer(1, cm)]
    for author in authors:
        story.append(Paragraph(escape(f"{author['nombre']} · {author['codigo']}"), styles['CoverText']))
    story += [Spacer(1, cm), Paragraph('Proyecto: mi_proyecto_routing', styles['CoverText']),
              Paragraph('Repositorio: https://github.com/JuniorPD04/practica_django', styles['CoverText'])]
    if url:
        story += [Paragraph(f'Servicio: {escape(url)}', styles['CoverText']),
                  Paragraph(f'Verificación pública: {escape(url)}/authors', styles['CoverText'])]
    else:
        story.append(Paragraph('PENDIENTE: desplegar y regenerar este PDF con --url antes de entregar.', styles['CoverText']))
    story += [Paragraph('Fecha de preparación: 13/11/2026', styles['CoverText']), PageBreak()]
    text = (folder / 'CUESTIONARIO.md').read_text(encoding='utf-8')
    for block in text.strip().split('\n\n'):
        if block.startswith('# '):
            story.append(Paragraph(escape(block[2:]), styles['Heading1']))
        elif block.startswith('## '):
            story.append(Paragraph(escape(block[3:]), styles['Heading2']))
        else:
            story.append(Paragraph(escape(block.replace('\n', ' ')), styles['BodyText']))

    def footer(canvas, doc):
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(colors.HexColor('#52616b'))
        canvas.drawString(2*cm, 1.2*cm, 'Desarrollo Web · Routing · Despliegue')
        canvas.drawRightString(A4[0]-2*cm, 1.2*cm, str(doc.page))

    doc = SimpleDocTemplate(str(output), pagesize=A4, rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=1.8*cm, bottomMargin=2*cm,
                            title='Despliegue Django - Equipo Routing',
                            author=', '.join(a['nombre'] for a in authors))
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f'PDF generado: {output}')
    if not url:
        print('Pendiente: regenerar con --url cuando el despliegue esté verificado.')


if __name__ == '__main__':
    main()
