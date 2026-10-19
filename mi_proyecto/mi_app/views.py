import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

def hola_mundo(request):
    return HttpResponse('¡Hola Mundo! - 407721')

# def pasar_kilo_a_libra(request, kilos):
#     libras = float(kilos) * 2.20462
#     return HttpResponse(f'{kilos} kilos son {libras:.2f} libras.')

def pasar_kilo_a_libra(request):
    kilos = request.GET.get('kilos', '0')
    try:
        kilos = float(kilos)
        libras = kilos * 2.20462
        return HttpResponse(f'{kilos} kilos son {libras:.2f} libras.')
    except ValueError:
        return HttpResponse('Por favor, ingrese un valor numérico válido para kilos.')

def clasificacion_edad(request):
    edad = request.GET.get('edad', '0')
    clasificado = ''
    try:
        edad = int(edad)
        if edad < 0:
            raise ValueError('La edad no puede ser negativa.')
        elif edad < 6:
            clasificado = 'Bebé'
        elif edad < 13:
            clasificado = 'Niño'
        elif edad < 21:
            clasificado = 'Adolescente'
        elif edad < 41:
            clasificado = 'Adulto joven'
        elif edad < 66:
            clasificado = 'Adulto'
        else:
            clasificado = 'Adulto mayor'

        return HttpResponse(f'La persona es {clasificado}.')

    except ValueError:
        return HttpResponse('Por favor, ingrese un valor numérico válido para edad.', status=400)

@csrf_exempt  
def contador_vocales(request):

    datos = json.loads(request.body.decode('utf-8'))
    texto = datos.get("texto")

    LISTA_NUMEROS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

    if any(char in LISTA_NUMEROS for char in str(texto)):
        return HttpResponse('El texto no debe contener números.', status=400)

    if request.method != 'POST':
        return HttpResponse('Método no permitido', status=405)

    LISTA_VOCAL = ['a', 'e', 'i', 'o', 'u']
    contador = 0

    for letra in texto.lower():
        if letra in LISTA_VOCAL:
            contador += 1

    return HttpResponse(f'El texto "{texto}" tiene {contador} vocales.')

@csrf_exempt
def frutas(request):

    if request.method != 'POST':
        return HttpResponse('Método no permitido', status=405)

    datos = json.loads(request.body.decode('utf-8'))
    frutas = list(datos.get("frutas"))

    if frutas == []:
        return HttpResponse('La lista de frutas está vacía.', status=400)

    frutas_ordenadas = sorted(frutas)
    fruta_mas_larga = max(frutas, key=len)
    fruta_mas_corta = min(frutas, key=len)

    return HttpResponse(f'Frutas ordenadas: {frutas_ordenadas}. \nFruta más larga: {fruta_mas_larga}. \nFruta más corta: {fruta_mas_corta}.')

def digitos_generador():
    import random
    digitos =random.randint(1000, 9999)
    return digitos

class Libro:
    def __init__(self, titulo, autor, genero):
        self.titulo = titulo
        self.autor = autor
        self.genero = genero
        self.issn = f"ISSN {digitos_generador()}-{digitos_generador()}"

@csrf_exempt
def libros(request):
    if request.method != 'POST':
        return HttpResponse('Método no permitido', status=405)

    libro = json.loads(request.body.decode('utf-8'))
    # libro = datos.get("libro")
    print(libro)

    if not isinstance(libro, dict) or 'titulo' not in libro or 'autor' not in libro or 'genero' not in libro:
        return HttpResponse('Cada libro debe ser un diccionario con "titulo", "autor" y "genero".', status=400)

    libro_objeto = Libro(titulo=libro.get("titulo"), autor=libro.get("autor"), genero=libro.get("genero"))

    libro_objeto = libro_objeto.__dict__

    return JsonResponse(libro_objeto, status=201)
