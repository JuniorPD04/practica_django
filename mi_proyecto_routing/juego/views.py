from django.shortcuts import render

# Create your views here.

# juego/views.py

import json

from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt

from django.views.decorators.http import require_http_methods


from .datos import PERSONAJES, HABILIDADES


@require_http_methods(['GET'])
def personajes_list(request):

    resultado = PERSONAJES
    nombre = request.GET.get('nombre')

    if nombre:
        n = nombre.lower()
        resultado = [p for p in resultado if n in p['nombre'].lower()]

    tipo = request.GET.get('tipo')
    if tipo:
        resultado = [p for p in resultado if p['tipo'] == tipo.lower()]

    return JsonResponse(resultado, safe=False, status=200)


@require_http_methods(['GET'])
def personaje_detail(request, id: int):

    for p in PERSONAJES:

        if p['id'] == id:

         return JsonResponse(p, status=200)

    return JsonResponse(

    {'error': 'Personaje no encontrado'}, status=404

    )


@csrf_exempt
@require_http_methods(['POST'])
def personajes_create(request):
    datos = json.loads(request.body)
    datos['id'] = len(PERSONAJES) + 1
    PERSONAJES.append(datos)
    return JsonResponse(datos, status=201)

@csrf_exempt
@require_http_methods(['GET', 'POST'])
def personajes_list_create(request):
    if request.method == 'GET':
        return personajes_list(request)
    elif request.method == 'POST':
        return personajes_create(request)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)


# Implementa personaje_update (PUT), personaje_delete (DELETE),

@csrf_exempt
@require_http_methods(['PUT'])
def personajes_update(request, id: int):
    datos = json.loads(request.body)
    
    encontrado = False
    for i, p in enumerate(PERSONAJES):
        if p['id'] == id:
            datos['id'] = id
            PERSONAJES[i] = datos
            encontrado = True
            break
            
    if not encontrado:
        return JsonResponse({'error': 'Personaje no encontrado'}, status=404)
        
    return JsonResponse(datos, status=200)

@csrf_exempt
@require_http_methods(['PUT', 'DELETE', 'GET'])
def personajes_detail_update_delete(request, id: int):
    if request.method == 'PUT':
        return personajes_update(request, id)
    elif request.method == 'DELETE':
        return personajes_delete(request, id)
    elif request.method == 'GET':
        return personaje_detail(request, id)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
@require_http_methods(['DELETE'])
def personajes_delete(request, id:int):

    encontrado = False
    for i, p in enumerate(PERSONAJES):
        if p['id'] == id:
            del PERSONAJES[i]
            encontrado = True
            break
    if not encontrado:
        return JsonResponse({'error': 'Personaje no encontrado'}, status=404)
    
    return JsonResponse({'mensaje':'Personaje de id {} eliminado'.format(id)}, status=204)

# y las mismas 5 vistas equivalentes para Habilidad.

@require_http_methods(['GET'])
def habilidades_list(request):
    resultado = HABILIDADES
    nombre = request.GET.get('nombre')
    orden = request.GET.get('orden')

    if nombre:
        n = nombre.lower()
        resultado = [p for p in resultado if n in p['nombre'].lower()]

    tipo = request.GET.get('tipo')
    if tipo:
        resultado = [p for p in resultado if p['tipo'] == tipo.lower()]

    if orden == 'estamina':
        resultado = sorted(resultado, key = lambda x: x['incremento_estamina'], reverse=True)

    return JsonResponse(resultado, safe=False, status=200)


@require_http_methods(['GET'])

def habilidad_detail(request, id: int):

    for p in HABILIDADES:

        if p['id'] == id:

         return JsonResponse(p, status=200)

    return JsonResponse(

    {'error': 'Habilidad no encontrada'}, status=404

    )


@csrf_exempt

@require_http_methods(['POST'])
def habilidad_create(request):

    datos = json.loads(request.body)

    datos['id'] = len(HABILIDADES) + 1

    HABILIDADES.append(datos)

    return JsonResponse(datos, status=201)

@csrf_exempt
@require_http_methods(['GET', 'POST'])
def habilidades_list_create(request):
    if request.method == 'GET':
        return habilidades_list(request)
    elif request.method == 'POST':
        return habilidad_create(request)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
@require_http_methods(['GET', 'PUT', 'DELETE'])
def habilidad_detail_update_delete(request, id: int):
    if request.method == 'GET':
        return habilidad_detail(request, id)
    elif request.method == 'PUT':
        return habilidad_update(request, id)
    elif request.method == 'DELETE':
        return habilidad_delete(request, id)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
@require_http_methods(['PUT'])
def habilidad_update(request, id: int):
    datos = json.loads(request.body)
    
    encontrado = False
    for i, h in enumerate(HABILIDADES):
        if h['id'] == id:
            datos['id'] = id
            HABILIDADES[i] = datos
            encontrado = True
            break
            
    if not encontrado:
        return JsonResponse({'error': 'Habilidad no encontrada'}, status=404)
        
    return JsonResponse(datos, status=200)

@csrf_exempt
@require_http_methods(['DELETE'])
def habilidad_delete(request, id:int):

    encontrado = False
    for i, h in enumerate(HABILIDADES):
        if h['id'] == id:
            del HABILIDADES[i]
            encontrado = True
            break
    if not encontrado:
        return JsonResponse({'error': 'Habilidad no encontrada'}, status=404)

    return JsonResponse({'mensaje':'Habilidad de id {} eliminada'.format(id)}, status=204)


@require_http_methods(['GET'])
def habilidades_de_personaje(request, id: int):
    personaje = next((p for p in PERSONAJES if p['id'] == id), None)
    if not personaje:
        return JsonResponse({'error': 'Personaje no encontrado'}, status=404)

    habilidades_personaje = [h for h in HABILIDADES if h['id'] in personaje.get('habilidades', [])]
    return JsonResponse(habilidades_personaje, safe=False, status=200)
