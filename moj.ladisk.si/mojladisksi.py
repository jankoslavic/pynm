import numpy as np
import os
import json
from sys import getsizeof
import requests

DOVOLJENI_TIPI = ['str', 'int', 'float', 'ndarray', 'tuple', 'list', 'dict']
MAX_LEN = 15
MAX_SIZE = 10e3 #bit

int_type_names = [dtype.__name__ for dtype in np.signedinteger.__subclasses__() + np.unsignedinteger.__subclasses__()] + ['int']
float_type_names = [dtype.__name__ for dtype in np.floating.__subclasses__()] + ['float', 'Float', 'Zero']

def pripravi_resitev(odgovor):
    """
    Funkcija pripravi rešitev za posredovanje na strežnik.

    Rezultat gre še skozi JSON, tako da vsebuje samo tipe, ki jih JSON pozna.
    Študentov odgovor gre čez JSON že ob pošiljanju, strežnik pa svojo rešitev
    izračuna lokalno in je ne serializira; brez tega bi tuple na strežniku ostal
    tuple, pri študentu pa bi postal list, in primerjava bi spodletela. Tip
    odgovora se ne izgubi, zapisan je v ključu 'tip'.
    """
    return json.loads(json.dumps(_pripravi_resitev(odgovor), default=data_to_json))


def _pripravi_resitev(odgovor):
    """
    Pripravi rešitev, preden gre skozi JSON (glej `pripravi_resitev`).
    Poimenovanje ključev je pomembno pri preverjanju odgovorov - naj se ne spreminja!
    Rezultat je: tip                (vsi)
                 vrednost           (NE ndarray)
                 dtype              (ndarray)
                 mean               (ndarray)
                 shape              (ndarray)
                 flat               (ndarray)
                 flat_size          (ndarray)
    """
    dovoljeni_tipi = ', '.join(DOVOLJENI_TIPI)
    out = dict()

    tip = type(odgovor).__name__

    if tip in int_type_names:
        out['tip'] = 'int'
        out['vrednost'] = int(odgovor)
        return out
    
    elif tip in float_type_names:
        out['tip'] = 'float'
        out['vrednost'] = float(odgovor)
        return out
    
    elif tip in ['str', 'list', 'tuple', 'dict']:
        bit_size = getsizeof(odgovor)
        if bit_size < MAX_SIZE:
            out['tip'] = tip
            out['vrednost'] = odgovor
            return out
        elif tip in ['list', 'tuple'] and len(odgovor) > MAX_LEN:
            korak = len(odgovor) // MAX_LEN + 1
            out['tip'] = tip
            out['korak'] = korak
            out['vrednost'] = odgovor[::korak]
            return out
        else:
            raise Exception(f'Napaka: Oddan odgovor, z velikostjo {bit_size/1e3:5.2f} kb, presega največjo dovoljeno velikost {MAX_SIZE/1e3:5.2f} kb.')
    
    elif tip in ['ndarray']:
        out.update(prepare_ndarray(odgovor))
        return out
    
    else:
        raise Exception('Napaka: rezultat tipa \'{0:s}\' ne ustreza pričakovanim tipom: {1:s}!'.format(tip, dovoljeni_tipi))


def prepare_ndarray(array, MAX_LEN=15):
    """
    Pripravi numpy.ndarray za oddajo - flatten, skrajša na MAX_LEN , pretvori v seznam 
    in zapakira v dict (tip:'ndarray', dtype, mean, shape, flat, flat_size).
    Poimenovanje ključev je pomembno pri preverjanju odgovorov - naj se ne spreminja!
    """
    flat = array.flatten()
    inc = 1
    if len(flat) > MAX_LEN:
        inc = len(flat) // MAX_LEN + 1
        flat = flat[::inc]
    flat_list = flat.tolist()
    return {
        'tip': 'ndarray',
        'dtype': array.dtype.name,
        'mean': np.mean(array),
        'shape': array.shape,
        'flat': flat_list,
        'flat_size': len(flat_list),
        'korak': inc
    }


def data_to_json(object):
    """
    Pripravi posredovan objekt za JSON serilizacijo. Uporabljen v primeru, ko
    pride do napake pri pretvorbi objekta v JSON.
    """
    if isinstance(object, np.ndarray):
        return prepare_ndarray(object)

    if isinstance(object, complex):
        return [object.real, object.imag]

    if type(object).__name__ in int_type_names:
        return int(object)

    if type(object).__name__ in float_type_names:
        return float(object)

    raise TypeError(f'Napaka pri pretvorbi podatka tipa {type(object)} v JSON. Preverite posredovan odgovor!')


def poslji(odgovor, id, st):
    """ Funkcija pošlje rešitev na strežnik.
    :param odgovor: spremenljivka nosilka odgovora
    :param id: identifikacijska številka naloge
    :param st: zaporedna številka odgovora
    """
    url = 'https://moj.ladisk.si/'
    client = requests.session()
    r = client.get(url + 'get_token')
    csrftoken = client.cookies['csrftoken']
    cookies = dict(client.cookies)
    headers = {'Content-type':'application/json', "X-CSRFToken":csrftoken, 'Referer':url}
    
    data = {
        'sa_id': id,
        'odgovor': pripravi_resitev(odgovor),
        'st': st,
       }

    json_data = json.dumps(data, default=data_to_json)

    r = requests.post(url + 'StudentData',
                        json=json_data, #json_data, če rabiš default data_to_json funkcijo
                        headers=headers,
                        cookies=cookies)

    # Odgovor strežnika izpišemo, ne vrnemo. Celice v nalogah kličejo `poslji(...)` brez
    # `print(...)`, Jupyter pa za zadnji izraz v celici izpiše `repr()`, zato bi se
    # večvrstično sporočilo izpisalo z vidnimi `\n` in narekovaji. Strežnik ob prvem
    # oddanem odgovoru v odprtem oknu sporoči tudi, da se je začel čas za reševanje, in
    # povezavo do odštevalnika, zato mora biti izpis večvrstičen.
    print(r.json()['status'])
