from bs4 import BeautifulSoup, Comment, Doctype
import re

section_regexp= r'^(Part|Title|Chapter|Section|Sub-Section|Article|ANNEX)\ *([0-9.]|ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN|ELEVEN|TWELVE|THIRTEEN|FOURTEEN|FIFTEEN|SIXTEEN|SEVENTEEN|EIGHTEEN|NINETEEN|TWENTY|I|II|III|IV|V|VI|VII|VIII|IX|X|X(I|II|III|IV|V|VI|VII|VIII|IX|X))* *$'

ANNEX_regexp= r'^(ANNEX)\ *([0-9.]|ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN|ELEVEN|TWELVE|THIRTEEN|FOURTEEN|FIFTEEN|SIXTEEN|SEVENTEEN|EIGHTEEN|NINETEEN|TWENTY|I|II|III|IV|V|VI|VII|VIII|IX|X|X(I|II|III|IV|V|VI|VII|VIII|IX|X))* *$'


def clean_html(  html_file  ):
    
    '''
    Function will find all text in the html, convert to a plain text (String), and will split up the String in sections using the section_regexp.
    
    :param html_file: String containing a html file in plain text.
    :return: List of Strings (articles). 
    '''
    
    page_content=BeautifulSoup( html_file, "html.parser")
    
    
    articles=[]
    article=[]
    
    
    #remove the header:
    [x.extract() for x in page_content.findAll('head')]

    #remove the items of Doctype type:
    for item in page_content:
        if isinstance(item, Doctype):
            item.extract()

    #remove the comments
    com = page_content.findAll(text=lambda text:isinstance(text, Comment))
    [comment.extract() for comment in com]

    for node in page_content.findAll('p'):
        text = ''.join(node.findAll(text=True)) 
        text = text.strip() 
        text= text.replace( "\n", "" )
        text= text.replace( "\xa0" , " ")
               
        if text:  
            if bool(re.match( section_regexp, text , re.IGNORECASE )):  #new_article
                articles.append( "\n".join(article)  )
                article=[]
            article.append( text )

    if article:
        articles.append( "\n".join(article)  )  #add the last article, or the first when no sections found  
            
    return articles


def clean_pdf( pdf_file  ):
    
    '''
    Function will split a document in articles using the section_regex.
    
    :param pdf_file: String containing a pdf file in plain text.
    :return: List of Strings (articles). 
    '''
    
    articles=[]
    article=[]
    
    pdf_file=pdf_file.strip( "\n" ).split("\n")
    
    for text in pdf_file:
        if text:
            if bool (re.match( section_regexp, text , re.IGNORECASE )):
                articles.append( "\n".join(article )  )
                article=[]
            article.append( text )
            
    if article:
        articles.append( "\n".join(article)  )  #add the last article, or the first when no sections found         

    return articles
    
    
def delete_annexes(articles):
    
    '''
    Function will delete all annexes from a list of articles obtained via clean_html or clean_pdf, using the ANNEX_regexp.
    
    :param articles: List containing articles (String).
    :return: List of Strings (articles). 
    '''
    
    
    #delete the annexes:
    articles_no_annexes=[]
    for article in articles:
        if bool(re.match( ANNEX_regexp,  article.strip("\n").split( "\n" )[0]  , re.IGNORECASE )):
            #continue
            break  #not adding annexes, or anything that comes after annex
        else:
            articles_no_annexes.append( article )
            
    return articles_no_annexes

