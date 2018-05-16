"""constants.py"""

# RIS

RIS_WSDL = 'realtimeservice2/services/RISService70?wsdl'
RIS_URL = 'realtimeservice2/services/RISService70'
RIS_QUERY_TEMPLATE = '''
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:soap="http://schemas.cisco.com/ast/soap">
   <soapenv:Header/>
   <soapenv:Body>
      <soap:selectCmDeviceExt>
         <soap:StateInfo></soap:StateInfo>
         <soap:CmSelectionCriteria>
            <soap:MaxReturnedDevices>1000</soap:MaxReturnedDevices>
            <soap:DeviceClass>Phone</soap:DeviceClass>
            <soap:Model>255</soap:Model>
            <soap:Status>Registered</soap:Status>
            <soap:NodeName></soap:NodeName>
            <soap:SelectBy>Name</soap:SelectBy>
            <soap:SelectItems>
               {% for devicename in devices %}
               <soap:item>
                  <soap:Item>{{ devicename }}</soap:Item>
               </soap:item>
               {% endfor %}
            </soap:SelectItems>
            <soap:Protocol>Any</soap:Protocol>
            <soap:DownloadStatus>Any</soap:DownloadStatus>
         </soap:CmSelectionCriteria>
      </soap:selectCmDeviceExt>
   </soapenv:Body>
</soapenv:Envelope>'''
RIS_NAMESPACE = '{http://schemas.cisco.com/ast/soap}'


## AXL

AXL_URL = 'axl/'
AXL_QUERY_TEMPLATE = '''
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns="http://www.cisco.com/AXL/API/10.0">
   <soapenv:Header/>
   <soapenv:Body>
      <ns:listPhone>
      <searchCriteria><name>SEP%</name></searchCriteria>
      <returnedTags><name></name><model></model></returnedTags>
      </ns:listPhone>
   </soapenv:Body>
</soapenv:Envelope>'''