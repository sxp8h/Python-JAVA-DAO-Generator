# Basic Java-DAO generator
import logging
import argparse

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

# Logging settings
# logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(message)s')
logging.addLevelName(logging.WARNING, "\033[1;93m%s\033[1;0m" % logging.getLevelName(logging.WARNING))
logging.addLevelName(logging.ERROR, "\033[1;91m%s\033[1;0m" % logging.getLevelName(logging.ERROR))
logging.addLevelName(logging.DEBUG, "\033[1;94m%s\033[1;0m" % logging.getLevelName(logging.DEBUG))
logging.addLevelName(logging.INFO, "\033[1;92m%s\033[1;0m" % logging.getLevelName(logging.INFO))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="Read from file for attributes")
    parser.add_argument("-e", "--example", help="Generate an example XML file")
    args = parser.parse_args()

    if args.file:
        get_current_file(args.file)

    if args.example:
        generate_standard_xml(args.example)


def generate_standard_xml(filename):
    logging.warning("[!] Generating {}.xml file".format(filename))
    filename += '.xml'
    example_file = open(filename, mode='w')
    example_xml = "<dao name='Artist'>" \
                  "\n\t<table name='TABLE_NAME' type='RED_ARTIST'></table>" \
                  "\n\t<table name='ID_ARTIST'></table>" \
                  "\n\t<table name='NAME'></table>" \
                  "\n\t<table name='URL'></table>" \
                  "\n\t<table name='NATIONALITY'></table>" \
                  "\n\t<attr name='id' type='int'></attr>" \
                  "\n\t<attr name='name' type='String'></attr>" \
                  "\n\t<attr name='url' type='String'></attr>" \
                  "\n\t<attr name='nationality' type='String'></attr>" \
                  "\n</dao>"
    example_file.write(example_xml)
    logging.warning("[!] {} file generated!".format(filename))


def get_current_file(filename):
    logging.warning("[!] Opening {}".format(filename))
    logging.debug("[-] File name: {}".format(filename))
    file = ET.parse(filename).getroot()
    global new_file
    global table
    global number_of_attribs
    for node in file.iter():
        # Getting root of xml and filename for .java

        if "dao" in node.tag:
            new_file = node.attrib['name'].title()

        # Getting 

        if "table" in node.tag:
            if "TABLE_NAME" in node.attrib['name']:
                tables.append(node.get('name') + ':' + node.get('type'))
                continue
            tables.append(node.get('name'))

        if "attr" in node.tag:
            attributes.append(node.get('name') + ":" + node.get('type'))
            number_of_attribs += 1

    generate_header()
    generate_sql()
    generate_attrib()
    generate_constructor()
    generate_getter_setter()
    generate_crud()
    save_file()


def generate_header():
    global new_file
    global file
    logging.debug("[!] Generating HEADER for file {}.java".format(new_file))
    sxp8h = "\n//\n"
    sxp8h += "//  ::::::::  :::    ::: :::::::::   ::::::::  :::    :::\n"
    sxp8h += "// :+:    :+: :+:    :+: :+:    :+: :+:    :+: :+:    :+:\n"
    sxp8h += "// +:+         +:+  +:+  +:+    +:+ +:+    +:+ +:+    +:+\n"
    sxp8h += "// +#++:++#++   +#++:+   +#++:++#+   +#++:++#  +#++:++#++\n"
    sxp8h += "//        +#+  +#+  +#+  +#+        +#+    +#+ +#+    +#+\n"
    sxp8h += "// #+#    #+# #+#    #+# #+#        #+#    #+# #+#    #+#\n"
    sxp8h += "//  ########  ###    ### ###         ########  ###    ###\n"
    sxp8h += "//\n"
    sxp8h += "//          --------Created by SXP8H--------           \n\n"

    package = "package beans;\n\n"

    imports = "import java.sql.Connection;\n"
    imports += "import java.sql.PreparedStatement;\n"
    imports += "import java.sql.ResultSet;\n"
    imports += "import java.util.logging.Level;\n"
    imports += "import java.util.logging.Logger;\n"
    imports += "import java.util.ArrayList;\n\n\n"

    class_entry = "public class {}".format(new_file)
    class_entry += '{\n'

    connection = '\t// Connection'
    connection += '\n\tprivate ConnectionOracle database = new ConnectionOracle();'
    connection += '\n\tprivate Connection con;\n'

    file = sxp8h + package + imports + class_entry + connection
    logging.debug("[!] Headers created!")


def generate_sql():
    global new_file
    global file
    global tables
    table_name = ''
    value_table_name = ''

    # Table part

    logging.debug("[!] Generating TABLES DECLARATIONS for file {}.java".format(new_file))
    line = '\n\t// TABLE {}\n'.format(new_file)

    for names in tables:
        if "TABLE_NAME" in names:
            names = names.split(":")
            table_name = names[0]
            value_table_name = names[1]
            line += '\tprivate final String {} = "{}";\n'.format(table_name, value_table_name)
            continue
        line += '\tprivate final String {} = "{}";\n'.format(names, names)

    file += line
    logging.debug("[!] TABLES DECLARATIONS created!")
    logging.debug("[!] Generating SQLHEADERS for file {}.java".format(new_file))

    line = '\n\t// Sql headers'

    #
    # SQL_CREATE
    #

    line += '\n\tprivate final String SQL_CREATE = "INSERT INTO " + {} + " ( '.format(table_name)

    # var i is used to jump 2 positions ( table_name & ID )
    i = 2
    for name in tables:

        if "TABLE_NAME" in name or "ID" in name:
            continue
        if i < (len(tables) - 1):
            line += '" + {} + ", '.format(name)
        else:
            line += '" + {} + " ) VALUES "; '.format(name)
        i += 1

    #
    # SQL_READ
    #

    line += '\n\tprivate final String SQL_READ = "SELECT * FROM " + {};'.format(table_name)

    #
    # SQL_UPDATE
    #

    line += '\n\tprivate final String SQL_UPDATE = "UPDATE " + {} + " SET ";'.format(table_name)

    #
    # SQL_DELETE
    #

    line += '\n\tprivate final String SQL_DELETE = "DELETE FROM " + {};\n'.format(table_name)

    file += line
    logging.debug("[!] SQLHEADERS created!")


def generate_attrib():
    global file
    global attributes

    logging.debug("[!] Generating Attributes for file {}.java".format(new_file))

    line = '\n\t// Attributes'

    for name in attributes:
        name = name.split(":")
        line += "\n\tprivate {} {};".format(name[1], name[0])

    file += line
    logging.debug("[!] ATTRIBUTES created!")


def generate_constructor():
    global file
    global new_file
    global attributes
    global number_of_attribs

    logging.debug("[!] Generating Constructors for file {}.java".format(new_file))

    line = '\n\n\t// Constructor'
    line += '\n\tpublic {}()'.format(new_file.title())
    line += '{}'
    line += "\n\tpublic {}(".format(new_file.title())

    i = 0

    for name in attributes:
        name = name.split(":")
        if "id" in name:
            continue
        if i < (number_of_attribs - 2):
            line += '{} {},'.format(name[1], name[0])
        else:
            line += ' {} {}) '.format(name[1], name[0])
        i += 1

    i = 1

    line += '{\n'

    for names in attributes:
        names = names.split(":")
        if "id" in names:
            continue

        line += '\t\tthis.{} = {};\n'.format(names[0], names[0])

        i += 1

    line += '\t}\n'
    file += line


def generate_getter_setter():
    global file
    global attributes

    logging.debug("[!] Generating Getters & Setters for file {}.java".format(new_file))
    line = '\n\n\t// Getters & Setters'

    for name in attributes:
        line += '\n\tpublic '
        name = name.split(":")
        line += '{} get{}() '.format(name[1], name[0].title())
        line += '{\n'
        line += '\t\treturn {};\n'.format(name[0], name[0])
        line += '\t}\n'

    for name in attributes:
        line += '\n\tpublic '
        name = name.split(":")
        line += 'void set{}({} {}) '.format(name[0].title(), name[1], name[0])
        line += '{\n'
        line += '\t\tthis.{} = {};\n'.format(name[0], name[0])
        line += '\t}\n'

    file += line
    logging.debug("[!] GETTERS&SETTERS created!")


def generate_crud():
    global file
    global attributes
    global new_file
    global number_of_attribs

    logging.debug("[!] Generating Methods for file {}.java".format(new_file))

    line = '\n\n\t// Methods'
    #
    # CREATE
    #

    line += '\n\tpublic int create({} bean)'.format(new_file)
    line += '{\n'
    line += '\t\tint result;\n'

    for at in attributes:
        if "id" in at:
            continue
        at = at.split(":")
        line += '\n\t\t{} {} = (bean.get{}() == null || bean.get{}().equals("")) ? "<EMPTY_{}>" : bean.get{}();'.format(
            at[1], at[0], at[0].title(), at[0].title(), at[0].upper(), at[0].title())

    line += '\n\t\tString sql = SQL_CREATE;\n'
    line += '\t\tsql += "( '

    i = 1

    for name in attributes:
        if "id" in name:
            continue
        if i < (number_of_attribs - 1):
            line += '?, '
        else:
            line += '? )";'
        i += 1

    line += '\n\t\ttry {'
    line += '\n\t\t\tcon = database.connect();'
    line += '\n\t\t\tPreparedStatement createSt = con.prepareStatement(sql);'

    i = 1

    for name in attributes:
        name = name.split(':')
        if "id" in name[0]:
            continue
        else:
            line += '\n\t\t\tcreateSt.set{}({}, {});'.format(name[1].title(), i, name[0])
        i += 1

    line += '\n\t\t\tresult = createSt.executeUpdate();'
    line += '\n\t\t} catch (Exception ex) {'
    line += '\n\t\t\tLogger.getLogger({}.class.getName()).log(Level.SEVERE, null, ex);'.format(new_file)
    line += '\n\t\t\treturn 1;'
    line += '\n\t\t}\n\t\treturn result;'
    line += '\n\t}'
    file += line

    line = ''
    #
    # READ
    #
    line = '\n\tpublic ArrayList<{}> read()'.format(new_file)
    line += '{\n'
    line += '\t\tArrayList<{}> result = new ArrayList();\n'.format(new_file)
    line += '\t\tResultSet rs;\n'
    line += '\t\tString sql = SQL_READ;\n'
    line += '\t\ttry {\n'
    line += '\t\t\tcon = database.connect();\n'
    line += '\t\t\tPreparedStatement readSt = con.prepareStatement(sql);\n'
    line += '\t\t\trs = readSt.executeQuery();\n\n'
    line += '\t\t\twhile(rs.next()){\n'
    line += '\t\t\t\t{} aux = new {}();\n\n'.format(new_file, new_file)

    aux = []
    get = []

    for attrib in attributes:
        attrib = attrib.split(':')
        aux.append('\t\t\t\taux.set{}(rs.get{}('.format(attrib[0].title(), attrib[1].title()))

    for table in tables:
        if 'TABLE_NAME' in table:
            continue
        get.append('{}));\n'.format(table))

    i = 0
    for i in range(number_of_attribs):
        line += '{}{}'.format(aux[i], get[i])
        i += 1

    line += '\t\t\t\tresult.add(aux);\n'
    line += '\t\t\t}\n'
    line += '\n\t\t} catch (Exception ex) {'
    line += '\n\t\t\tLogger.getLogger({}.class.getName()).log(Level.SEVERE, null, ex);'.format(new_file)
    line += '\n\t\t\treturn null;'
    line += '\n\t\t}\n\t\treturn result;'
    line += '\n\t}'
    file += line

    #
    # READ(int id)
    #
    line = '\n\tpublic ArrayList<{}> read(int id)'.format(new_file)
    line += '{\n'
    line += '\t\tArrayList<{}> result = new ArrayList();\n'.format(new_file)
    line += '\t\tResultSet rs;\n'
    for table in tables:
        if 'table_name' in table:
            continue
        if 'ID' in table:
            line += '\t\tString sql = SQL_READ + " WHERE " + {} + " = ?";\n'.format(table)
            break
    line += '\t\ttry {\n'
    line += '\t\t\tcon = database.connect();\n'
    line += '\t\t\tPreparedStatement readSt = con.prepareStatement(sql);\n'
    for at in attributes:
        at = at.split(':')
        if 'id' in at[0]:
            line += '\t\t\treadSt.set{}(1, id);\n'.format(at[1].title())
            break
    line += '\t\t\trs = readSt.executeQuery();\n\n'

    line += '\t\t\twhile(rs.next()){\n'
    line += '\t\t\t\t{} aux = new {}();\n\n'.format(new_file, new_file)

    aux = []
    get = []

    for attrib in attributes:
        attrib = attrib.split(':')
        aux.append('\t\t\t\taux.set{}(rs.get{}('.format(attrib[0].title(), attrib[1].title()))
    for table in tables:
        if 'TABLE_NAME' in table:
            continue
        get.append('{}));\n'.format(table))

    i = 0
    for i in range(number_of_attribs - 1):
        line += '{}{}'.format(aux[i], get[i])
        i += 1

    line += '\t\t\t\tresult.add(aux);\n'
    line += '\t\t\t}\n'
    line += '\n\t\t} catch (Exception ex) {'
    line += '\n\t\t\tLogger.getLogger({}.class.getName()).log(Level.SEVERE, null, ex);'.format(new_file)
    line += '\n\t\t\treturn null;'
    line += '\n\t\t}\n\t\treturn result;'
    line += '\n\t}'
    file += line

    #
    # UPDATE
    #
    line = '\n\tpublic int update({} bean)'.format(new_file)
    line += '{\n'
    line += '\t\tint result;\n'

    for at in attributes:
        at = at.split(":")
        if "id" in at:
            line += '\n\t\t{} {} = bean.get{}();'.format(at[1], at[0], at[0].title())
            continue
        line += '\n\t\t{} {} = (bean.get{}() == null || bean.get{}().equals("")) ? "<EMPTY_{}>" : bean.get{}();'.format(
            at[1], at[0], at[0].title(), at[0].title(), at[0].upper(), at[0].title())

    line += '\n\n\t\tString sql = SQL_UPDATE;'
    line += '\n\t\tsql += " " + '

    i = 2
    for tab in tables:
        if 'TABLE_NAME' in tab:
            continue
        if 'ID' in tab:
            continue
        if i < (len(tables) - 1):
            line += ' {} + " = ?, " +'.format(tab)
        else:
            line += ' {} + " = ?";\n'.format(tab)
        i += 1

    for tabb in tables:
        if 'TABLE_NAME' in tabb:
            continue
        if 'ID' in tabb:
            line += '\t\tsql += " WHERE " + {} + " = ?";\n'.format(tabb)
            break

    line += '\n\t\ttry {'
    line += '\n\t\t\tcon = database.connect();'
    line += '\n\t\t\tPreparedStatement updateSt = con.prepareStatement(sql);'

    i = 1

    for name in attributes:
        name = name.split(':')
        if "id" in name[0]:
            line2 = '\n\t\t\tupdateSt.set{}({}, {});'.format(name[1].title(), len(attributes), name[0])
            continue
        else:
            line += '\n\t\t\tupdateSt.set{}({}, {});'.format(name[1].title(), i, name[0])
        i += 1
    line += line2
    line += '\n\n\t\t\tresult = updateSt.executeUpdate();'

    line += '\n\t\t} catch (Exception ex) {'
    line += '\n\t\t\tLogger.getLogger({}.class.getName()).log(Level.SEVERE, null, ex);'.format(new_file)
    line += '\n\t\t\treturn 1;'
    line += '\n\t\t}'
    line += '\n\n\t\treturn result;'
    line += '\n\t}'

    file += line

    #
    # DELETE(int id)
    #
    line = '\n\tpublic int delete(int id){'
    line += '\n\t\tint result;'
    line += '\n\t\tString sql = SQL_DELETE + " WHERE " + '
    for row in tables:
        if 'ID' in row:
            line += '{} + " = ?";'.format(row)
            break

    line += '\n\t\ttry {'
    line += '\n\t\t\tcon = database.connect();'
    line += '\n\t\t\tPreparedStatement deleteSt = con.prepareStatement(sql);'
    line += '\n\t\t\tdeleteSt.setInt(1, id);'
    line += '\n\t\t\tresult = deleteSt.executeUpdate();'
    line += '\n\t\t} catch (Exception ex) {'
    line += '\n\t\t\tLogger.getLogger({}.class.getName()).log(Level.SEVERE, null, ex);'.format(new_file)
    line += '\n\t\t\treturn 1;'
    line += '\n\t\t}'
    line += '\n\n\t\treturn result;'
    line += '\n\t}'

    line += '\n}'

    file += line
    logging.debug("[!] METHODS created!")


def save_file():
    global file
    global new_file
    logging.warning('[!] Saving file')
    new_file += '.java'
    open_file = open(new_file, 'w')
    open_file.writelines(file)
    open_file.close
    logging.warning('[*] File created!!')


# Declare vars used on the program
attributes = []
number_of_attribs = 0
new_file = None
tables = []
file = None

# Start of program
main()