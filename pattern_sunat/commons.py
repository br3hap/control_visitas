# -*- coding: utf-8 -*-

import logging

from lxml import etree
from .except_error import WebServiceError

from requests import Session
from zeep import Client as ClientZepp
from zeep.transports import Transport


WS_PADRON = {
    'URL_NOMBRE':'URL_PADRON',
    'NOMBRE_METODO_PADRON': 'NOMBRE_METODO_PADRON',
    'CUERPO_TRAMA_PADRON': 'wsConsulta',
    'TIPO_CONSULTA':'tipoConsulta',
    'RUC':'ruc',
    }

VALUES = {
        'EXITO':'1',
        'ERROR':'0',
    }

TAGS_PADRON_RESPUESTA = {
    'COD_ERROR':'codError',
    'LST_EMPR':'lstEmpresas',
    'COD_ZONA':'codzona',
    'COND_DOMIC':'condiciondomic',
    'DEPARTAMENTO':'departamento',
    'ESTADO':'estado',
    'INTERIOR':'interior',
    'KM':'kilometro',
    'LOTE':'lote',
    'MANZANA':'manzana',
    'NOMBRE':'nombre',
    'NOMB_VIA':'nomvia',
    'NUMERO':'numero',
    'RUC':'ruc',
    'TIPO_VIA':'tipovia',
    'TIPO_ZONA':'tipozona',
    'UBIGEO_TAG':'ubigeo',
    'COD_UBIGEO':'codigoUbigeo',
    'DEPARTAMENTO':'departamento',
    'DISTRITO':'distrito',
    'PROVINCIA':'provincia',
    }

def get_tag_text(resp, tag):
    content = False
    for child in resp.iterchildren():
        if (not content) :
            if(child.countchildren() > 0) :
                content = get_tag_text(child, tag)
            else :
                if child.tag == tag:
                    content = child.text
    return content

# Función que valida que el dato exista y crea el tag con el texto mandado como parametro
def valida_y_crea(obj, tag, txt, Sub):
    
    if isinstance(txt, float):
        txt = str('%.2f' % txt)
        if txt == 'False':
            txt = False
        
    if isinstance(txt, int) :
        txt = str(txt)
        if txt == 'False':
            txt = False
        
    if txt:
        child = etree.Element(tag)
        child.text = txt
    
        if Sub:
            obj.append(child)
        else:
            return child
    
def get_respuesta_zeep(url, metodo, trama):
    """
        Método que consume un servicio .wsdl
        
        :param str url: direccion donde se encuentra expuesto el método
        :param str metodo: nombre del metodo a consumir
        :param str trama: data que consume el metodo
        :returns: 
    """
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('zeep.transport').setLevel(logging.DEBUG)
    #logging.getLogger('suds.xsd.schema').setLevel(logging.DEBUG)
    #logging.getLogger('suds.wsdl').setLevel(logging.DEBUG)
    
    try:
        session = Session()
        session.verify = False
        transport = Transport(session=session)
        cliente = ClientZepp(url, transport=transport)
        return getattr(cliente.service, metodo)(trama)
    except Exception as e:
        raise WebServiceError(e)