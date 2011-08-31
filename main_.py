#!/usr/bin/env python

import os
import re
import time
import random
import platform
import shutil
from ConfigParser import ConfigParser

import RSSparse
import PAGEparse
import OPFgen

def writeFile(filename,open_type,write_content):
  action = open(filename,open_type)
  action.write(write_content)
  action.close()
  
def randomString(count):
  basestring = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
  return "".join(random.sample(basestring,count))
  
def makeDir(directory):
  if not os.path.isdir(directory):
    os.makedirs(directory)
  else:
    pass
    
def compareFilename(filename_base,ebook_type,publ_dir):
  filename = filename_base + "." + ebook_type
  if os.path.isfile(os.path.join(publ_dir,filename)):
    filename1 = filename_base + "-" + randomString(6) + "." + ebook_type
  else:
    filename1 = filename
  return os.path.join(publ_dir,filename1)

def genEpub(work_dir,filename_base,publ_dir):
  filename = filename_base + ".epub"
  command1 = "zip -0Xq " + filename + " mimetype"
  command2 = "zip -Xr9Dq " + filename + " *"
  os.chdir(work_dir)
  os.system(command1)
  os.system(command2)
  filename_dest = compareFilename(filename_base,"epub",publ_dir)
  shutil.move(filename,filename_dest)

def genMobi(work_dir,filename_base,publ_dir):
  param = " -c1 -verbose -o "
  filename = filename_base + ".mobi"
  command = "kindlegen " + "content.opf " + param + filename
  os.chdir(work_dir)
  os.system(command)
  filename_dest = compareFilename(filename_base,"mobi",publ_dir)
  shutil.move(filename,filename_dest)
  
def mailSend(mail_from,mail_to,attachment):
  subject = attachment
  message = "BR/mobi book generated by mobi.pagebrin.com"
  if not len(mail_to) == 0:
    if mail_from:
      mail_from = " ".join(["-r",mail_from])
    command = " ".join(["echo",message,"|","mail","-s",subject,"-a",attachment,mail_from,mail_to])
    os.system(command)
  else:
    pass
  
def main():
  # read the config file.
  config_file = "config.cfg"
  config = ConfigParser()
  config.read(config_file)
  
  mail_enable  = config.get("SYSTEM","mail enable")
  mail_from    = config.get("SYSTEM","mail from")
  mail_to      = config.get("SYSTEM","mail to")
  base_dir     = config.get("SYSTEM","base directory")
  temp_dir     = config.get("SYSTEM","temp directory")
  image_dir    = config.get("SYSTEM","image directory")
  publ_dir     = config.get("SYSTEM","publish directory")
  res_dir      = config.get("SYSTEM","resource directory")
  config_file  = os.path.join(base_dir,"config.cfg")
  
  makeDir(publ_dir)
  makeDir(image_dir)
  
  config_list = config.sections()
  rss_list    = [i for i in config_list if re.search(r"RSS",i)]
  for item in rss_list:
    title        = config.get(item,"title")
    creator      = config.get(item,"creator")
    publisher    = config.get(item,"publisher")
    source       = config.get(item,"source")
    rights       = config.get(item,"rights")
    subject      = config.get(item,"subject")
    description  = config.get(item,"description")
    contributor  = config.get(item,"contributor")
    type2        = config.get(item,"type2")
    format2      = config.get(item,"format2")
    identifier   = config.get(item,"identifier")
    language     = config.get(item,"language")
    relation     = config.get(item,"relation")
    coverage     = config.get(item,"coverage")

    url                = config.get(item,"rss_url")
    findall_key        = config.get(item,"findall key")
    find_key           = config.get(item,"find key")
    pageparse_keyword  = config.get(item,"pageparse keyword")
    handle_weekday     = config.get(item,"handle weekday")

    date      = time.strftime("%Y-%m-%d", time.localtime())
    date_week = time.strftime("%Y%W", time.localtime())
    find_key  = find_key.split(",")
    bookid    = randomString(12)
    
    title2   = title + "-" + date_week

    # generate the url of this week's nfpeople
    if re.search(r'nfpeople',title):
      uri = str(int(time.strftime("%W", time.localtime())) + 8)
      uri = "Magazine-detail-item-" + uri + ".html"
      url += uri
    
    collection = "rss_" + title
    # RSS parse and write into database.
    content = RSSparse.fetchHtml(url)
    if re.search(r'nfpeople',url):
      list_today = RSSparse.fetchListNFpeople(content)
    else:
      list_today = RSSparse.fetchList(content,findall_key,find_key)
    for line in list_today:
      if not RSSparse.isqueryDB(collection,line["link"]):
        html_content = RSSparse.fetchHtml(line["link"])
        if not html_content:
          RSSparse.insertDB(collection,line,errorno = 1)
          continue
        page = PAGEparse.pageFormat(html_content,pageparse_keyword)
        if not page:
          RSSparse.insertDB(collection,line,errorno = 2)
          continue
        if re.search(r'nfpeople',title):
          page = PAGEparse.pageFormatNFpeople(page)
        
        # down image in html enties. 
        os.chdir(image_dir)
        dic = PAGEparse.downloadIMG(page,title)
        
        #os.chdir(oebps_dir)
        page_addbodytag = PAGEparse.addBodytag(dic["entire"])
        page_entire = PAGEparse.htmlHeader() + page_addbodytag
        doc = {}
        doc["html"] = page_entire
        doc["image"] = dic["image"]
        doc.update(line)
        RSSparse.insertDB(collection,doc,errorno = 0)
    
    weekday = time.strftime("%w", time.localtime())
    if weekday != handle_weekday:
      continue
    else:
      pass
    
    # PAGE parse
    list_index = RSSparse.queryDB(collection)
    # if list_index is blank, skip it.
    if not list_index:
      continue


    # down html file and image.
    # create directory for OEBPS-temp file. 
    temp_dir = os.path.join(temp_dir,str(int(time.time())))
    oebps_dir = os.path.join(temp_dir,"OEBPS")
    makeDir(oebps_dir)
    os.chdir(oebps_dir)
    index = 1
    list_index1 = RSSparse.queryDB(collection)
    for i in list_index1:
      out_filename = str(index) + ".html"
      PAGEparse.writeHtml(out_filename,i["html"].encode("utf-8"))
      image_pathto = os.path.join(oebps_dir,"images")
      makeDir(image_pathto)
      for j in i["image"]:
        image_pathfrom = os.path.join(image_dir,j)
        shutil.copy(image_pathfrom,image_pathto)
      index += 1
      # update database's is_operate value.
      RSSparse.updateDB(collection,i['link'])

    # OPF generation
    opf_metadata = OPFgen.opfMetadata(item,config_file)
    opf_entire = OPFgen.opfHeader(bookid) + opf_metadata + OPFgen.opfMainfest(list_index1) + OPFgen.opfSpine(list_index1) + OPFgen.opfGuide() + OPFgen.opfFooter()
    opf_filename = "content.opf"
    writeFile(opf_filename,"w",opf_entire)

    # INDEX html file generation
    html_header = OPFgen.htmlHeader()
    html_body = OPFgen.htmlBody(list_index1)
    html_body = OPFgen.addBodytag(html_body)
    index_entire = html_header + html_body
    html_filename = "0.html"
    writeFile(html_filename,"w",index_entire)

    # TOC.ncx generation
    ncx_header = OPFgen.ncxHeader()
    ncx_head = OPFgen.ncxHead(bookid)
    ncx_doctitle = OPFgen.ncxDocTitle(title2)
    ncx_docauthor = OPFgen.ncxDocAuthor(creator)
    ncx_entirenavpoint = OPFgen.ncxEntireNavPoint(list_index1)
    ncx_navmap = OPFgen.ncxNavMap(ncx_entirenavpoint)
    ncx_body = ncx_head + ncx_doctitle + ncx_docauthor + ncx_navmap
    ncx_body = OPFgen.ncxBody(ncx_body)
    ncx_entire = ncx_header + ncx_body
    ncx_filename = "toc.ncx"
    writeFile(ncx_filename,"w",ncx_entire)
    
    # copy structure files.
    mimetype_path = os.path.join(res_dir,"mimetype")
    stylesheet_path = os.path.join(res_dir,"stylesheet.css")
    metainf_path = os.path.join(res_dir,"META-INF")
    shutil.copy(mimetype_path,temp_dir)
    shutil.copy(stylesheet_path,os.path.join(temp_dir,"OEBPS"))
    shutil.copytree(metainf_path,os.path.join(temp_dir,"META-INF"))
    
    
    # genaration the epub book.
    genEpub(temp_dir,title2,publ_dir)

    # genaration the mobi book use system tool kindlegen
    genMobi(oebps_dir,title2,publ_dir)
    
    # mail mobi book as attachment to specified mail address.
    if mail_enable == "yes":
      os.chdir(publ_dir)
      attachment = title2 + ".mobi"
      mailSend(mail_from,mail_to,attachment)

if __name__ == "__main__":
  main()
