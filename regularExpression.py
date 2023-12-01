import re
pattern = "wiki"
text = '''A wiki (/ˈwɪki/ ⓘ WIK-ee) is a form of online hypertext publication, collaboratively edited and managed by its own audience, using a web browser. A typical wiki contains multiple pages for the subjects or scope of the project, and could be either open to the public or limited to use within an organization for maintaining its internal knowledge base.

Wikis are enabled by wiki software, otherwise known as wiki engines. A wiki engine, being a form of a content management system, differs from other web-based systems such as blog software, in that the content is created without any defined owner or leader, and wikis have little inherent structure, allowing structure to emerge according to the needs of the users.[1] Wiki engines usually allow content to be written using a simplified markup language and sometimes edited with the help of a rich-text editor.[2] There are dozens of different wiki engines in use, both standalone and part of other software, such as bug tracking systems. Some wiki engines are free and open-source, whereas others are proprietary. Some permit control over different functions (levels of access); for example, editing rights may permit changing, adding, or removing material. Others may permit access without enforcing access control. Further rules may be imposed to organize content.'''
#match = re.search(pattern, text) #only for one time usage
#print(match)

matches = re.finditer(pattern,text)
for match in matches:
    print(match.span())