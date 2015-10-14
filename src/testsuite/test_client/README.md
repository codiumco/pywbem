End-to-end testing for the PyWBEM client
========================================

This directory contains YAML files that are test cases for testing the PyWBEM
client end-to-end.

Each YAML file contains a list of test cases.

The test_client.py test module will iterate through the YAML files in this
directory, and execute each testcase in each file.

Example YAML
------------

The following YAML is an example for one testcase in such a file:

    -
        name: demo1
        description: Demo #1, using GetInstance
        pywbem_request:
            url: http://acme.com:80
            creds:
                - username
                - password
            namespace: root/cimv2
            timeout: 10
            debug: false
            operation:
                pywbem_method: GetInstance
                InstanceName:
                    pywbem_object: CIMInstanceName
                    classname: PyWBEM_Person
                    keybindings:
                        Name: Fritz
                LocalOnly: false
        pywbem_response:
            result:
                pywbem_object: CIMInstance
                classname: PyWBEM_Person
                properties:
                    Name: Fritz
                    Address: Fritz Town
                path:
                    pywbem_object: CIMInstanceName
                    classname: PyWBEM_Person
                    namespace: root/cimv2
                    keybindings:
                        Name: Fritz
        http_request:
            verb: POST
            url: http://acme.com:80/cimom
            headers:
                CIMOperation: MethodCall
                CIMMethod: GetInstance
                CIMObject: root/cimv2
            data: >
                <?xml version="1.0" encoding="utf-8" ?>
                <CIM CIMVERSION="2.0" DTDVERSION="2.0">
                  <MESSAGE ID="1001" PROTOCOLVERSION="1.0">
                    <SIMPLEREQ>
                      <IMETHODCALL NAME="GetInstance">
                        <LOCALNAMESPACEPATH>
                          <NAMESPACE NAME="root"/>
                          <NAMESPACE NAME="cimv2"/>
                        </LOCALNAMESPACEPATH>
                        <IPARAMVALUE NAME="InstanceName">
                          <INSTANCENAME CLASSNAME="PyWBEM_Person">
                            <KEYBINDING NAME="Name">
                              <KEYVALUE VALUETYPE="string">Fritz</KEYVALUE>
                            </KEYBINDING>
                          </INSTANCENAME>
                        </IPARAMVALUE>
                        <IPARAMVALUE NAME="LocalOnly">
                          <VALUE>False</VALUE>
                        </IPARAMVALUE>
                      </IMETHODCALL>
                    </SIMPLEREQ>
                  </MESSAGE>
                </CIM>
        http_response:
            status: 200
            headers:
                Content-Type: application/xml
            data: >
                <?xml version="1.0" encoding="utf-8" ?>
                <CIM CIMVERSION="2.0" DTDVERSION="2.0">
                  <MESSAGE ID="1001" PROTOCOLVERSION="1.0">
                    <SIMPLERSP>
                      <IMETHODRESPONSE NAME="GetInstance">
                        <IRETURNVALUE>
                          <INSTANCE CLASSNAME="PyWBEM_Person">
                            <PROPERTY NAME="Name" TYPE="string">
                              <VALUE>Fritz</VALUE>
                            </PROPERTY>
                            <PROPERTY NAME="Address" TYPE="string">
                              <VALUE>Fritz Town</VALUE>
                            </PROPERTY>
                          </INSTANCE>
                        </IRETURNVALUE>
                      </IMETHODRESPONSE>
                    </SIMPLERSP>
                  </MESSAGE>
                </CIM>

Top-level elements
------------------

The top-level elements in the test case YAML are:

* `name`:
  A name for the test case that is used in error messages.

* `description`:
  A short description of the testcase.

* `pywbem_request`:
  A specification of the PyWBEM client function to test, and the input
  arguments for its invocation.

* `pywbem_response`:
  A specification of the expected result of the PyWBEM client function that is
  being tested. It is possible to specify expected CIM status codes, other
  Python exceptions, or the resulting object in case of success.

* `http_request`:
  A specification of the expected HTTP request the PyWBEM client produced
  for the client function that is being tested. This includes the first line
  of the HTTP request, any HTTP headers, and the CIM body data (the CIM-XML)

* `http_response`:
  The HTTP response for the PyWBEM client function that will be handed back
  to the client function that is being tested.
  It is possible to specify successful eresponses, error responses, and even
  inconsistent or illegal responses in order to verify how the client handles
  those.

Elements in `pywbem_request` element
------------------------------------

* `url`, `creds`, `namespace`, `timeout`:
  The same-named arguments of pywbem.WBEMConnection()

* `debug`:
  Boolean indicating whether the PyWBEM client enables debug mode.

* `operation`:
  A specification of the WBEMConnection method (= CIM operation) to be
  invoked. Its child elements are:

  * `pywbem_method`:
    Name of the Python method of pywbem.WBEMConnection as a string
    (e.g. "GetInstance").

  * arguments for that Python method. Each element has the argument's name.

    If its Python type is boolean, string, or numerical, the element's
    value is directly the desired argument value.

    Otherwise, the element has child elements that specify how the Python
    object is constructed, as follows:

    * `pywbem_object`:
      Name of the Python type to construct (i.e. the constructor), as a string.
      (e.g. "CIMInstanceName").

    * arguments for that constructor. Each element has the argument's name. This
      can be nested at arbitraty depth, see the description of the arguments one
      level up.

Elements in `pywbem_response` element
-------------------------------------

* `cim_status`:
  The numerical expected CIM status code of the operation.
  This is optional; if not specified, it defaults to 0 (=Success).

* `exception`:
  The name of the Python exception that is expectd to be raised.
  This is optional; if not specified, it defaults to None (=no exception is
  raised).

* `result`:
  A specification of the expected result (= return value) of the operation,
  implying that the operation succeeded.

  If the Python type of the result is boolean, string, or numerical, the
  element's value is directly the desired argument value.

  Otherwise, the element has child elements that specify how the Python
  object is constructed, as follows:

  * `pywbem_object`:
    Name of the Python type to construct (i.e. the constructor), as a string.
    (e.g. "CIMInstanceName").

  * arguments for that constructor. Each element has the argument's name. This
    can be nested at arbitraty depth, see the description of the arguments one
    level up.

Elements in `http_request` element
------------------------------------

* `verb`:
  The expected HTTP verb / method the PyWBEM client issues (e.g. "POST").

* `url`:
  The expected URL the PyWBEM client targets the HTTP request to
  (e.g. "http://acme.com:80/cimom").
  Note that this is the url specified as an argument to pywbem.WBEMConnection,
  appended with "/cimom".

* `headers`:
  The expected HTTP header fields in the HTTP request. Only the onese specified
  here are verified, others may be present and will not be verified.

  The name of the element is the header field name, and its value is the
  header field value. Header field names are treated case insensitively.

* `data`:
  The expected CIM-XML payload of the request. When comparing the actual CIM-XML
  to the expected CIM-XML, whitespace in between XML elements (tags) and
  attributes are being ignored.

Elements in `http_response` element
-------------------------------------

* `status`:
  The numerical HTTP status in the HTTP response handed back to the PyWBEM
  client (e.g. 200).

* `headers`:
  The HTTP header fields in the HTTP response handed back to the PyWBEM
  client.

  TBD: Does HTTPretty have any standard header fields it adds?

  The name of the element is the header field name, and its value is the
  header field value. Header field names are treated case insensitively.

* `data`:
  The CIM-XML payload in the HTTP response handed back to the PyWBEM
  client. The CIm-XML is handed back as resulting from the specified
  YAML, including any whitespace.