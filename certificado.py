import re, xml.etree.ElementTree as ETree, datetime
from cairosvg import svg2pdf

def parse_data():
	data_separator = "\t"
	join_separators = True
	separator = re.compile(data_separator+('+'*join_separators))
	data_list = column_name = []
	data_last = {}
	data_file = open('certificado.data','r')
	for line in data_file.readlines():
		if len(column_name):
			splitted_line = separator.split(line,columns)
			[splitted_line.append('') for n in range(columns-len(splitted_line))]
			column = 0
			data_dict = {}
			while column < columns:
				data_dict[column_name[column]] = splitted_line[column].rstrip("\n")
				if(data_dict[column_name[column]]==""):
					try:
						data_dict[column_name[column]] = data_last[column_name[column]]
					except:
						pass
				column = column + 1
			data_list.append(data_dict)
			data_last = data_dict
		else:
			column_name = separator.split(line.rstrip("\n"))
			columns = len(column_name)
	data_file.close()
	return data_list

def replace_svg(file_name,replace_dict={},output_file=None):
	svg_tree=ETree.parse(file_name)
	svg_root=svg_tree.getroot()
	for child in svg_root.iter():
		for replace_key in replace_dict.keys():
			if( child.text and re.sub('\|[^>]*','',child.text) == '<'+replace_key+'>' ):
				print(child.text,replace_dict[replace_key])
				replace_value = replace_dict[replace_key]
				filter_functions = re.findall('\|filter(\w+)',child.text)
				if 'noDefaults' not in filter_functions:
					filter_functions.append('Default')
				for filter_function in filter_functions:
					print('filter: ',filter_function)
					if globals().get('filter'+filter_function):
						replace_value=globals()['filter'+filter_function](replace_value)
					else:
						print('¡ Filter '+filter_function+' not Found !')
				child.text = replace_value
				if(output_file):
					svg_tree.write(output_file)
				else:
					return svg_tree.tostring(encoding='utf-8')

def filterTitleCase(name):
	lambda_lower_re_matches=lambda matches:str.lower(matches.group(0))
	return re.sub(r'\b(D((a|e|o)s?|i)?|E|V(o|a)n)\b',lambda_lower_re_matches,name.title())

def filterLowerCase(text):
	return text.lower()

def filterDefault(text):
	return text
			
for data_set in parse_data():
	temp_svg_file='/tmp/_svg2pdf_'+data_set['NOME'].replace(' ','_')+'.svg'
	replace_svg("certificado.svg",data_set,temp_svg_file)
	svg2pdf(url=temp_svg_file,write_to='output/'+data_set['NOME'].replace(' ','_')+'.pdf')

