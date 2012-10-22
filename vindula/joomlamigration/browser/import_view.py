# -*- coding: utf-8 -*-
import transaction
from datetime import datetime
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
import pdb
from pprint import pprint
from urllib2 import urlopen
from unicodedata import normalize
import base64, httplib, urllib2
from import_models import *
from DateTime.DateTime import DateTime
from zope.app.component.hooks import getSite
from random import randint
import re
import urllib2
from urlparse import urlsplit

store = getStore()

def url_to_params(url):
    for ch in ['&','?']:
        if ch in url:
            url = url.replace(ch,'|')
    
    steps = url.split('|')
    params = {}
    for step in steps:
        if '=' in step:
            step = step.split('=')
            params[step[0]] = step[1]
    
    return params


class ImportJoomla(BrowserView):
    
    url_joomla = ''
    
    def createContent(self, store_obj=None, context=None):
        if not context:
            context = getSite()
            
        #Checa se existe o conteudo no contexto
        if context.get(store_obj.alias, None):
            print 'O objeto ja existe'
        else:
            conteudo = {}
            text_store = store_obj.introtext + store_obj.fulltext
            found_img = re.findall('img .*?src="(.*?)"', text_store)
            
            for img in found_img:
                url_img = self.url_joomla + img.replace(' ', '%20')
                try:
                    page_img = urllib2.urlopen(url=url_img, timeout=4)
                    if page_img:
                        new_img = page_img.read()
                        objeto = {'type_name':'Image',
                                  'id': img.split('/')[-1],
                                  'title': img.split('/')[-1],
                                  'image': new_img}
                        
                        obj_img = context.invokeFactory(**objeto)
                        obj_img = context[obj_img]
                        text_store = text_store.replace(img, obj_img.absolute_url_path())
                except:
                    pass
            
            conteudo['title'] = store_obj.title
            conteudo['id'] = store_obj.alias
            conteudo['text'] = text_store
            conteudo['state'] = store_obj.state
            
            obj = context.invokeFactory( type_name='VindulaNews',
                                         id=conteudo['id'],
                                         title=conteudo['title'],
                                         text=conteudo['text'],)
            
            obj = context[obj]
            print "Conteudo criado: %s" % obj.absolute_url_path()
            return obj
        
        return None
    
    def importContents(self):
        form = self.request.form
        if form.get('importa'):
            url_from = form.get('url_from', None)
            if url_from:
                try:
                    if url_from[-1] != '/': url_from=url_from+'/'
                    urllib2.urlopen(url=url_from, timeout=4)
                    
                    self.url_joomla = url_from
                    #Busca todos os menus da base do joomla
                    result_menus = store.find(Menu).order_by(Menu.sublevel, Menu.parent, Menu.ordering)
                    for menu in result_menus:
                        self.importMenu(menu=menu)
                except:
                    print 'URL Incorreta'
                    return
        
    def importMenu(self,
                   menu=None,
                   context=None):
        if not context:
            context = getSite()
        
        #Cria pasta 
        children_menus = store.find(Menu,
                                    Menu.parent==menu.id,
                                    Menu.sublevel==menu.sublevel+1,).order_by(Menu.ordering)
        
        
        try:                            
            obj = context.invokeFactory( type_name='VindulaFolder',
                                         id=menu.alias,
                                         title=menu.name,)
        except:
            obj = context.invokeFactory( type_name='VindulaFolder',
                                         id=menu.alias+str(randint(0,100)),
                                         title=menu.name,)
        
        context = context[obj]
        try:
            estado_obj = context.portal_workflow.getInfoFor(context,'review_state')    
            if estado_obj == 'private' and menu.published == 1:
                context.portal_workflow.doActionFor(context, 'publish')
        except: pass
        
        params_link = url_to_params(menu.link)
        view = params_link.get('view', '')
        id = params_link.get('id', '')
        
        if view.lower() == 'article':
            if id:
                result = store.find(Conteudo, Conteudo.id == int(id))
                result = result.one()
                if result:
                    obj_content = self.createContent(result, context)
                    context.setDefaultPage(obj_content.id)
                    estado_obj = obj_content.portal_workflow.getInfoFor(obj_content,'review_state')    
                    if estado_obj == 'private' and result.state == 1:
                        obj_content.portal_workflow.doActionFor(obj_content, 'publish')
                    
        elif view.lower() == 'category':
            if id:
                result = store.find(Conteudo, Conteudo.catid == int(id), Conteudo.state >= 0).order_by(Conteudo.ordering)
                for item in result:
                    try:
                        obj_content = self.createContent(item, context)
                        try:
                            estado_obj = obj_content.portal_workflow.getInfoFor(obj_content,'review_state')    
                            if estado_obj == 'private' and item.state == 1:
                                obj_content.portal_workflow.doActionFor(obj_content, 'publish')
                                print 'Objeto publicado: %s' % obj_content.id
                        except: pass
                    except:
                        pass
                    
        
        print (menu.sublevel+1)*'\t',menu.name,'|',menu.sublevel,'\n'
        
        for child_menu in children_menus:
            self.importMenu(menu=child_menu, context=context)
        
        return True

        
        
        
        
        
        
        
        if result_menus:
            for menu in result_menus:
                params_link = url_to_params(menu.link)
                view = params_link.get('view', '')
                
                if menu.sublevel == 0:
                    if view.lower() == 'article':
                        id = params_link.get('id', '')
                        if id:
                            conteudo = {}
                            result = store.find(Conteudo, Conteudo.id == int(id))
                            if result:
                                result = result.one()
                                obj = self.createContent(result, portal_obj)
                                
                    elif view.lower() == 'category':
                        folder = {}
                        folder['title'] = menu.name
                        folder['id'] = menu.alias
                        folder['state'] = menu.published
                        
                        obj = portal_obj.invokeFactory( type_name='VindulaFolder',
                                                        id=folder['id'],
                                                        title=folder['title'],)
                        
                        context = portal_obj[obj]
                        print "Pasta criado: %s" % context.absolute_url_path()

                        id = params_link.get('id', '')
                        if id:
                            result = store.find(Conteudo, Conteudo.catid == int(id))
                            for item in result:
                                obj = self.createContent(item, context)
                                
                                
    
    def getContentsJoomla(self):
        result = []
        
        #Busca todos os artigos da base do joomla
        result_menus = store.find(Menu).order_by(Menu.sublevel, Menu.parent, Menu.ordering)
        for menu in result_menus:
            
            
            result.append(content)
        
        
        result_store = store.find(Conteudo).order_by(Conteudo.catid, Conteudo.ordering, Conteudo.state)
        for content in result_store:
            result.append(content)
            
        return result