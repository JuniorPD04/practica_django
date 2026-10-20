# juego/datos.py


HABILIDADES = [

{

'id': 1,

'nombre': 'Espadazo',

'descripcion': 'Un ataque poderoso con la espada.',

'incremento_ataque': 10,

'incremento_defensa': 0,

'incremento_estamina': -5,

},

{

'id': 2,

'nombre': 'Escudo de Hierro',

'descripcion': 'Aumenta la defensa del guerrero.',

'incremento_ataque': 0,

'incremento_defensa': 15,

'incremento_estamina': -3,

},

# Agrega al menos 4 habilidades más.


{
    'id': 3,
    'nombre': 'Bola de Fuego',
    'descripcion': 'Lanza una bola de fuego que causa gran daño.',
    'incremento_ataque': 20,
    'incremento_defensa': 0,
    'incremento_estamina': -10,
},
{
    'id': 4,
    'nombre': 'Curacion Magica',
    'descripcion': 'Recupera energia y fortalece la resistencia.',
    'incremento_ataque': 0,
    'incremento_defensa': 10,
    'incremento_estamina': 15,
},
{
    'id': 5,
    'nombre': 'Flecha Veloz',
    'descripcion': 'Dispara una flecha rapida y precisa.',
    'incremento_ataque': 15,
    'incremento_defensa': 0,
    'incremento_estamina': -5,
},
{
    'id': 6,
    'nombre': 'Ataque Furtivo',
    'descripcion': 'Realiza un ataque sorpresa contra el enemigo.',
    'incremento_ataque': 25,
    'incremento_defensa': -5,
    'incremento_estamina': -10,
},
{
    'id': 7,
    'nombre': 'Piel de Piedra',
    'descripcion': 'Endurece la piel para resistir ataques enemigos.',
    'incremento_ataque': 0,
    'incremento_defensa': 25,
    'incremento_estamina': -8,
},

]


PERSONAJES = [

{

'id': 1,

'nombre': 'Gagh-Ar',

'tipo': 'guerrero',

'descripcion': 'Un valiente luchador con gran fuerza física.',

'ataque': 80, 'defensa': 70, 'estamina': 60,

'habilidades': [1, 2],

},

{

'id': 2,

'nombre': 'Elyra',

'tipo': 'maga',

'descripcion': 'Hechicera con gran dominio de la energía mágica.',

'ataque': 65, 'defensa': 40, 'estamina': 90,

'habilidades': [2],

},

# Agrega al menos 4 personajes más, con tipos variados.


{
    'id': 3,
    'nombre': 'Thalion',
    'tipo': 'elfo',
    'descripcion': 'Arquero experto con gran precision y agilidad.',
    'ataque': 75,
    'defensa': 50,
    'estamina': 85,
    'habilidades': [5, 4],
},
{
    'id': 4,
    'nombre': 'Zarek',
    'tipo': 'asesino',
    'descripcion': 'Guerrero sigiloso especializado en ataques rapidos.',
    'ataque': 90,
    'defensa': 35,
    'estamina': 80,
    'habilidades': [6, 5],
},
{
    'id': 5,
    'nombre': 'Brondar',
    'tipo': 'enano',
    'descripcion': 'Resistente luchador que domina el combate cuerpo a cuerpo.',
    'ataque': 70,
    'defensa': 95,
    'estamina': 55,
    'habilidades': [2, 7],
},
{
    'id': 6,
    'nombre': 'Lyanna',
    'tipo': 'arquera',
    'descripcion': 'Experta en ataques a distancia y movimientos veloces.',
    'ataque': 85,
    'defensa': 45,
    'estamina': 90,
    'habilidades': [5, 6],
},
{
    'id': 7,
    'nombre': 'Drogath',
    'tipo': 'orco',
    'descripcion': 'Poderoso combatiente conocido por su fuerza y resistencia.',
    'ataque': 95,
    'defensa': 80,
    'estamina': 65,
    'habilidades': [1, 7],
},

]