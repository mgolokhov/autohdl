import base64
import os
import sys
from lib import tinydav
from lib.tinydav.exception import HTTPUserError
from webdav import authenticate
from lxml import etree
t = '''
<D:multistatus xmlns:D="DAV:" xmlns:ns0="DAV:">
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype><D:collection/></lp1:resourcetype>
<lp1:creationdate>2011-08-23T14:59:51Z</lp1:creationdate>
<lp1:getlastmodified>Tue, 23 Aug 2011 14:59:51 GMT</lp1:getlastmodified>
<lp1:getetag>"19f8002-1000-4ab2d7293a7c0"</lp1:getetag>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
<D:getcontenttype>httpd/unix-directory</D:getcontenttype>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/circle_ring_20110722171342_top_ctrl_v3.mcs</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype/>
<lp1:creationdate>2011-08-19T19:59:03Z</lp1:creationdate>
<lp1:getcontentlength>465405</lp1:getcontentlength>
<lp1:getlastmodified>Fri, 22 Jul 2011 13:13:43 GMT</lp1:getlastmodified>
<lp1:getetag>"19f8003-719fd-4a8a83c17afc0"</lp1:getetag>
<lp3:executable>F</lp3:executable>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/dcs_server_simple_build_3.bit</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype/>
<lp1:creationdate>2011-08-19T19:59:03Z</lp1:creationdate>
<lp1:getcontentlength>169300</lp1:getcontentlength>
<lp1:getlastmodified>Mon, 02 May 2011 17:30:14 GMT</lp1:getlastmodified>
<lp1:getetag>"19f8004-29554-4a24e60525580"</lp1:getetag>
<lp3:executable>F</lp3:executable>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/top_ctrl_v4_build_2.mcs</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype/>
<lp1:creationdate>2011-08-19T19:59:03Z</lp1:creationdate>
<lp1:getcontentlength>465405</lp1:getcontentlength>
<lp1:getlastmodified>Fri, 22 Jul 2011 19:25:15 GMT</lp1:getlastmodified>
<lp1:getetag>"19f8005-719fd-4a8ad6ccc9cc0"</lp1:getetag>
<lp3:executable>F</lp3:executable>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/circle_ring_20110722161522_top_ctrl_v3.bit</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype/>
<lp1:creationdate>2011-08-19T19:59:03Z</lp1:creationdate>
<lp1:getcontentlength>169294</lp1:getcontentlength>
<lp1:getlastmodified>Fri, 22 Jul 2011 12:15:23 GMT</lp1:getlastmodified>
<lp1:getetag>"19f8006-2954e-4a8a76b79ecc0"</lp1:getetag>
<lp3:executable>F</lp3:executable>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/dcs_pult_arm2_2_6_1.mcs</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype/>
<lp1:creationdate>2011-08-19T19:59:03Z</lp1:creationdate>
<lp1:getcontentlength>465404</lp1:getcontentlength>
<lp1:getlastmodified>Tue, 19 Apr 2011 15:27:15 GMT</lp1:getlastmodified>
<lp1:getetag>"19f8007-719fc-4a147248fdac0"</lp1:getetag>
<lp3:executable>F</lp3:executable>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/dcs_pult_arm2_build_2.bit</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype/>
<lp1:creationdate>2011-08-19T19:59:03Z</lp1:creationdate>
<lp1:getcontentlength>169296</lp1:getcontentlength>
<lp1:getlastmodified>Mon, 02 May 2011 18:14:34 GMT</lp1:getlastmodified>
<lp1:getetag>"19f8008-29550-4a24efedeb680"</lp1:getetag>
<lp3:executable>F</lp3:executable>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/circle_ring_20110722111954_top_ctrl_v3.mcs</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype/>
<lp1:creationdate>2011-08-19T19:59:03Z</lp1:creationdate>
<lp1:getcontentlength>465405</lp1:getcontentlength>
<lp1:getlastmodified>Fri, 22 Jul 2011 07:19:56 GMT</lp1:getlastmodified>
<lp1:getetag>"19f8009-719fd-4a8a34add5f00"</lp1:getetag>
<lp3:executable>F</lp3:executable>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/vga_stripes_top.bit</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype/>
<lp1:creationdate>2011-08-19T19:59:03Z</lp1:creationdate>
<lp1:getcontentlength>283875</lp1:getcontentlength>
<lp1:getlastmodified>Sat, 16 Jul 2011 13:07:39 GMT</lp1:getlastmodified>
<lp1:getetag>"19f800a-454e3-4a82f73593cc0"</lp1:getetag>
<lp3:executable>F</lp3:executable>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/circle_ring_20110722162914_top_ctrl_v3.mcs</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype/>
<lp1:creationdate>2011-08-19T19:59:03Z</lp1:creationdate>
<lp1:getcontentlength>465405</lp1:getcontentlength>
<lp1:getlastmodified>Fri, 22 Jul 2011 12:29:15 GMT</lp1:getlastmodified>
<lp1:getetag>"19f800b-719fd-4a8a79d113cc0"</lp1:getetag>
<lp3:executable>F</lp3:executable>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/dcs_pult_arm2_build_1.mcs</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype/>
<lp1:creationdate>2011-08-19T19:59:03Z</lp1:creationdate>
<lp1:getcontentlength>465404</lp1:getcontentlength>
<lp1:getlastmodified>Mon, 02 May 2011 13:05:55 GMT</lp1:getlastmodified>
<lp1:getetag>"19f800c-719fc-4a24aaf0d32c0"</lp1:getetag>
<lp3:executable>F</lp3:executable>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/circle_ring_20110722111952_top_ctrl_v3.bit</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype/>
<lp1:creationdate>2011-08-19T19:59:03Z</lp1:creationdate>
<lp1:getcontentlength>169294</lp1:getcontentlength>
<lp1:getlastmodified>Fri, 22 Jul 2011 07:19:53 GMT</lp1:getlastmodified>
<lp1:getetag>"19f800d-2954e-4a8a34aaf9840"</lp1:getetag>
<lp3:executable>F</lp3:executable>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/dcs_pult_arm2_1_1_2.mcs</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype/>
<lp1:creationdate>2011-08-19T19:59:03Z</lp1:creationdate>
<lp1:getcontentlength>465404</lp1:getcontentlength>
<lp1:getlastmodified>Sat, 30 Apr 2011 14:26:35 GMT</lp1:getlastmodified>
<lp1:getetag>"19f800e-719fc-4a22393dafcc0"</lp1:getetag>
<lp3:executable>F</lp3:executable>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/circle_ring_20110722171322_top_ctrl_v3.mcs</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype/>
<lp1:creationdate>2011-08-19T19:59:03Z</lp1:creationdate>
<lp1:getcontentlength>465405</lp1:getcontentlength>
<lp1:getlastmodified>Fri, 22 Jul 2011 13:13:23 GMT</lp1:getlastmodified>
<lp1:getetag>"19f800f-719fd-4a8a83ae682c0"</lp1:getetag>
<lp3:executable>F</lp3:executable>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/top_ctrl_v4_build_1.bit</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype/>
<lp1:creationdate>2011-08-19T19:59:03Z</lp1:creationdate>
<lp1:getcontentlength>169294</lp1:getcontentlength>
<lp1:getlastmodified>Fri, 22 Jul 2011 19:08:43 GMT</lp1:getlastmodified>
<lp1:getetag>"19f8010-2954e-4a8ad31abe4c0"</lp1:getetag>
<lp3:executable>F</lp3:executable>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/dcs_pult_arm2_1_1_2.bit</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype/>
<lp1:creationdate>2011-08-19T19:59:03Z</lp1:creationdate>
<lp1:getcontentlength>169302</lp1:getcontentlength>
<lp1:getlastmodified>Sat, 30 Apr 2011 14:26:33 GMT</lp1:getlastmodified>
<lp1:getetag>"19f8011-29556-4a22393bc7840"</lp1:getetag>
<lp3:executable>F</lp3:executable>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/dcs_pult_arm2_1_1_1.mcs</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype/>
<lp1:creationdate>2011-08-19T19:59:03Z</lp1:creationdate>
<lp1:getcontentlength>465404</lp1:getcontentlength>
<lp1:getlastmodified>Sat, 30 Apr 2011 14:18:54 GMT</lp1:getlastmodified>
<lp1:getetag>"19f8012-719fc-4a2237860af80"</lp1:getetag>
<lp3:executable>F</lp3:executable>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/dcs_server_simple_build_1.bit</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype/>
<lp1:creationdate>2011-08-19T19:59:03Z</lp1:creationdate>
<lp1:getcontentlength>169300</lp1:getcontentlength>
<lp1:getlastmodified>Mon, 02 May 2011 14:15:54 GMT</lp1:getlastmodified>
<lp1:getetag>"19f8013-29554-4a24ba954da80"</lp1:getetag>
<lp3:executable>F</lp3:executable>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/dcs_server_simple_build_4.bit</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype/>
<lp1:creationdate>2011-08-19T19:59:03Z</lp1:creationdate>
<lp1:getcontentlength>169300</lp1:getcontentlength>
<lp1:getlastmodified>Mon, 02 May 2011 18:48:31 GMT</lp1:getlastmodified>
<lp1:getetag>"19f8014-29554-4a24f7848ddc0"</lp1:getetag>
<lp3:executable>F</lp3:executable>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/doka_circle/</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype><D:collection/></lp1:resourcetype>
<lp1:creationdate>2011-08-19T19:59:04Z</lp1:creationdate>
<lp1:getlastmodified>Mon, 25 Jul 2011 13:13:28 GMT</lp1:getlastmodified>
<lp1:getetag>"19f8015-1000-4a8e494b8ee00"</lp1:getetag>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
<D:getcontenttype>httpd/unix-directory</D:getcontenttype>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/pult_arm_starter/</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype><D:collection/></lp1:resourcetype>
<lp1:creationdate>2011-08-19T19:59:04Z</lp1:creationdate>
<lp1:getlastmodified>Tue, 02 Aug 2011 06:25:58 GMT</lp1:getlastmodified>
<lp1:getetag>"19f803d-1000-4a97fd21e8980"</lp1:getetag>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
<D:getcontenttype>httpd/unix-directory</D:getcontenttype>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/dcs_server_simple_build_3.mcs</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype/>
<lp1:creationdate>2011-08-19T19:59:04Z</lp1:creationdate>
<lp1:getcontentlength>465404</lp1:getcontentlength>
<lp1:getlastmodified>Mon, 02 May 2011 17:30:13 GMT</lp1:getlastmodified>
<lp1:getetag>"19f803f-719fc-4a24e60431340"</lp1:getetag>
<lp3:executable>F</lp3:executable>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/dcs_server_simple_2_6_1.mcs</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype/>
<lp1:creationdate>2011-08-19T19:59:04Z</lp1:creationdate>
<lp1:getcontentlength>465404</lp1:getcontentlength>
<lp1:getlastmodified>Tue, 19 Apr 2011 15:49:08 GMT</lp1:getlastmodified>
<lp1:getetag>"19f8040-719fc-4a14772d2a500"</lp1:getetag>
<lp3:executable>F</lp3:executable>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/top_ctrl_v4_build_0.mcs</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype/>
<lp1:creationdate>2011-08-19T19:59:04Z</lp1:creationdate>
<lp1:getcontentlength>465405</lp1:getcontentlength>
<lp1:getlastmodified>Fri, 22 Jul 2011 17:44:24 GMT</lp1:getlastmodified>
<lp1:getetag>"19f8041-719fd-4a8ac0421ae00"</lp1:getetag>
<lp3:executable>F</lp3:executable>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/usb_server/</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype><D:collection/></lp1:resourcetype>
<lp1:creationdate>2011-08-23T14:59:53Z</lp1:creationdate>
<lp1:getlastmodified>Tue, 23 Aug 2011 14:59:53 GMT</lp1:getlastmodified>
<lp1:getetag>"1a783bf-1000-4ab2d72b22c40"</lp1:getetag>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
<D:getcontenttype>httpd/unix-directory</D:getcontenttype>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/top_dcs2_epson.mcs</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype/>
<lp1:creationdate>2011-08-19T19:59:04Z</lp1:creationdate>
<lp1:getcontentlength>465404</lp1:getcontentlength>
<lp1:getlastmodified>Mon, 30 May 2011 14:48:22 GMT</lp1:getlastmodified>
<lp1:getetag>"19f8042-719fc-4a47f60ff7980"</lp1:getetag>
<lp3:executable>F</lp3:executable>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/dcs_server_simple_build_2.bit</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype/>
<lp1:creationdate>2011-08-19T19:59:04Z</lp1:creationdate>
<lp1:getcontentlength>169300</lp1:getcontentlength>
<lp1:getlastmodified>Mon, 02 May 2011 16:00:31 GMT</lp1:getlastmodified>
<lp1:getetag>"19f8043-29554-4a24d1f7845c0"</lp1:getetag>
<lp3:executable>F</lp3:executable>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/pult_arm/</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype><D:collection/></lp1:resourcetype>
<lp1:creationdate>2011-08-21T17:03:52Z</lp1:creationdate>
<lp1:getlastmodified>Sun, 21 Aug 2011 17:03:52 GMT</lp1:getlastmodified>
<lp1:getetag>"19f8044-1000-4ab06f2698e00"</lp1:getetag>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
<D:getcontenttype>httpd/unix-directory</D:getcontenttype>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/top_circle_ring_ctrl_v3.mcs</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype/>
<lp1:creationdate>2011-08-19T19:59:04Z</lp1:creationdate>
<lp1:getcontentlength>465405</lp1:getcontentlength>
<lp1:getlastmodified>Mon, 11 Jul 2011 11:57:45 GMT</lp1:getlastmodified>
<lp1:getetag>"19f804b-719fd-4a7c9e4290040"</lp1:getetag>
<lp3:executable>F</lp3:executable>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/test_nokia_lcd/</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype><D:collection/></lp1:resourcetype>
<lp1:creationdate>2011-08-19T19:59:04Z</lp1:creationdate>
<lp1:getlastmodified>Tue, 10 May 2011 18:21:00 GMT</lp1:getlastmodified>
<lp1:getetag>"19f804c-1000-4a2f0049b9b00"</lp1:getetag>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
<D:getcontenttype>httpd/unix-directory</D:getcontenttype>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/top_dcs2_epson.bit</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype/>
<lp1:creationdate>2011-08-19T19:59:04Z</lp1:creationdate>
<lp1:getcontentlength>169314</lp1:getcontentlength>
<lp1:getlastmodified>Mon, 30 May 2011 14:48:20 GMT</lp1:getlastmodified>
<lp1:getetag>"19f8051-29562-4a47f60e0f500"</lp1:getetag>
<lp3:executable>F</lp3:executable>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/dcs_pult_arm2_build_1.bit</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype/>
<lp1:creationdate>2011-08-19T19:59:04Z</lp1:creationdate>
<lp1:getcontentlength>169296</lp1:getcontentlength>
<lp1:getlastmodified>Mon, 02 May 2011 13:05:56 GMT</lp1:getlastmodified>
<lp1:getetag>"19f8052-29550-4a24aaf1c7500"</lp1:getetag>
<lp3:executable>F</lp3:executable>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/dcs_server_simple_2_2_2.mcs</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype/>
<lp1:creationdate>2011-08-19T19:59:04Z</lp1:creationdate>
<lp1:getcontentlength>465404</lp1:getcontentlength>
<lp1:getlastmodified>Tue, 19 Apr 2011 13:46:44 GMT</lp1:getlastmodified>
<lp1:getetag>"19f8053-719fc-4a145bd161900"</lp1:getetag>
<lp3:executable>F</lp3:executable>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/vga_stripes_top_build_1.bit</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype/>
<lp1:creationdate>2011-08-19T19:59:04Z</lp1:creationdate>
<lp1:getcontentlength>131033</lp1:getcontentlength>
<lp1:getlastmodified>Fri, 06 May 2011 19:07:34 GMT</lp1:getlastmodified>
<lp1:getetag>"19f8054-1ffd9-4a2a033c72980"</lp1:getetag>
<lp3:executable>F</lp3:executable>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/top_ctrl_v4_build_2.bit</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype/>
<lp1:creationdate>2011-08-19T19:59:04Z</lp1:creationdate>
<lp1:getcontentlength>169294</lp1:getcontentlength>
<lp1:getlastmodified>Fri, 22 Jul 2011 19:25:13 GMT</lp1:getlastmodified>
<lp1:getetag>"19f8055-2954e-4a8ad6cae1840"</lp1:getetag>
<lp3:executable>F</lp3:executable>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/dcs_server_simple_2_6_1.bit</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype/>
<lp1:creationdate>2011-08-19T19:59:04Z</lp1:creationdate>
<lp1:getcontentlength>169323</lp1:getcontentlength>
<lp1:getlastmodified>Tue, 19 Apr 2011 15:49:05 GMT</lp1:getlastmodified>
<lp1:getetag>"19f8056-2956b-4a14772a4de40"</lp1:getetag>
<lp3:executable>F</lp3:executable>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/dcs_server_simple_build_2.mcs</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype/>
<lp1:creationdate>2011-08-19T19:59:04Z</lp1:creationdate>
<lp1:getcontentlength>465404</lp1:getcontentlength>
<lp1:getlastmodified>Mon, 02 May 2011 16:00:29 GMT</lp1:getlastmodified>
<lp1:getetag>"19f8057-719fc-4a24d1f59c140"</lp1:getetag>
<lp3:executable>F</lp3:executable>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/vga_stripes_top_build_1.mcs</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype/>
<lp1:creationdate>2011-08-19T19:59:04Z</lp1:creationdate>
<lp1:getcontentlength>360168</lp1:getcontentlength>
<lp1:getlastmodified>Fri, 06 May 2011 19:07:33 GMT</lp1:getlastmodified>
<lp1:getetag>"19f8058-57ee8-4a2a033b7e740"</lp1:getetag>
<lp3:executable>F</lp3:executable>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/dcs_server_simple.bit</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype/>
<lp1:creationdate>2011-08-19T19:59:04Z</lp1:creationdate>
<lp1:getcontentlength>169300</lp1:getcontentlength>
<lp1:getlastmodified>Sun, 01 May 2011 18:42:31 GMT</lp1:getlastmodified>
<lp1:getetag>"19f8059-29554-4a23b44fc53c0"</lp1:getetag>
<lp3:executable>F</lp3:executable>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/circle_ring/</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype><D:collection/></lp1:resourcetype>
<lp1:creationdate>2011-08-21T16:02:02Z</lp1:creationdate>
<lp1:getlastmodified>Sun, 21 Aug 2011 16:02:02 GMT</lp1:getlastmodified>
<lp1:getetag>"19f805a-1000-4ab0615477280"</lp1:getetag>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
<D:getcontenttype>httpd/unix-directory</D:getcontenttype>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/dcs_server_simple.mcs</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype/>
<lp1:creationdate>2011-08-19T19:59:04Z</lp1:creationdate>
<lp1:getcontentlength>465404</lp1:getcontentlength>
<lp1:getlastmodified>Sun, 01 May 2011 18:42:33 GMT</lp1:getlastmodified>
<lp1:getetag>"19f805d-719fc-4a23b451ad840"</lp1:getetag>
<lp3:executable>F</lp3:executable>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/dcs_pult_arm2_2_6_1.bit</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype/>
<lp1:creationdate>2011-08-19T19:59:04Z</lp1:creationdate>
<lp1:getcontentlength>169319</lp1:getcontentlength>
<lp1:getlastmodified>Tue, 19 Apr 2011 15:27:12 GMT</lp1:getlastmodified>
<lp1:getetag>"19f805e-29567-4a14724621400"</lp1:getetag>
<lp3:executable>F</lp3:executable>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/evbfpga_dcs_server/</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype><D:collection/></lp1:resourcetype>
<lp1:creationdate>2011-08-19T19:59:04Z</lp1:creationdate>
<lp1:getlastmodified>Mon, 01 Aug 2011 20:30:53 GMT</lp1:getlastmodified>
<lp1:getetag>"19f805f-1000-4a97781ef7940"</lp1:getetag>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
<D:getcontenttype>httpd/unix-directory</D:getcontenttype>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/top_ctrl_v4_build_1.mcs</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype/>
<lp1:creationdate>2011-08-19T19:59:04Z</lp1:creationdate>
<lp1:getcontentlength>465405</lp1:getcontentlength>
<lp1:getlastmodified>Fri, 22 Jul 2011 19:08:45 GMT</lp1:getlastmodified>
<lp1:getetag>"19f8062-719fd-4a8ad31ca6940"</lp1:getetag>
<lp3:executable>F</lp3:executable>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/dcs_server_simple_build_1.mcs</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype/>
<lp1:creationdate>2011-08-19T19:59:05Z</lp1:creationdate>
<lp1:getcontentlength>465404</lp1:getcontentlength>
<lp1:getlastmodified>Mon, 02 May 2011 14:15:53 GMT</lp1:getlastmodified>
<lp1:getetag>"19f8063-719fc-4a24ba9459840"</lp1:getetag>
<lp3:executable>F</lp3:executable>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/dcs_2/</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype><D:collection/></lp1:resourcetype>
<lp1:creationdate>2011-08-21T16:40:06Z</lp1:creationdate>
<lp1:getlastmodified>Sun, 21 Aug 2011 16:40:06 GMT</lp1:getlastmodified>
<lp1:getetag>"19f8064-1000-4ab069d6a8580"</lp1:getetag>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
<D:getcontenttype>httpd/unix-directory</D:getcontenttype>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/circle_ring_20110722161523_top_ctrl_v3.mcs</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype/>
<lp1:creationdate>2011-08-19T19:59:05Z</lp1:creationdate>
<lp1:getcontentlength>465405</lp1:getcontentlength>
<lp1:getlastmodified>Fri, 22 Jul 2011 12:15:25 GMT</lp1:getlastmodified>
<lp1:getetag>"19f806f-719fd-4a8a76b987140"</lp1:getetag>
<lp3:executable>F</lp3:executable>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/circle_ring_20110722162912_top_ctrl_v3.bit</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype/>
<lp1:creationdate>2011-08-19T19:59:05Z</lp1:creationdate>
<lp1:getcontentlength>169294</lp1:getcontentlength>
<lp1:getlastmodified>Fri, 22 Jul 2011 12:29:13 GMT</lp1:getlastmodified>
<lp1:getetag>"19f8070-2954e-4a8a79cf2b840"</lp1:getetag>
<lp3:executable>F</lp3:executable>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/top_circle_ring_ctrl_v3.bit</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype/>
<lp1:creationdate>2011-08-19T19:59:05Z</lp1:creationdate>
<lp1:getcontentlength>169294</lp1:getcontentlength>
<lp1:getlastmodified>Mon, 11 Jul 2011 11:57:38 GMT</lp1:getlastmodified>
<lp1:getetag>"19f8071-2954e-4a7c9e3be3080"</lp1:getetag>
<lp3:executable>F</lp3:executable>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/dcs_server/</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype><D:collection/></lp1:resourcetype>
<lp1:creationdate>2011-09-23T16:22:50Z</lp1:creationdate>
<lp1:getlastmodified>Fri, 23 Sep 2011 16:22:50 GMT</lp1:getlastmodified>
<lp1:getetag>"19f8072-1000-4ad9e386dca80"</lp1:getetag>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
<D:getcontenttype>httpd/unix-directory</D:getcontenttype>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/vga_stripes_top_build_2.bit</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype/>
<lp1:creationdate>2011-08-19T19:59:06Z</lp1:creationdate>
<lp1:getcontentlength>283858</lp1:getcontentlength>
<lp1:getlastmodified>Sun, 08 May 2011 16:35:22 GMT</lp1:getlastmodified>
<lp1:getetag>"19f8079-454d2-4a2c64f26a680"</lp1:getetag>
<lp3:executable>F</lp3:executable>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/dcs_server_simple_build_4.mcs</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype/>
<lp1:creationdate>2011-08-19T19:59:06Z</lp1:creationdate>
<lp1:getcontentlength>465404</lp1:getcontentlength>
<lp1:getlastmodified>Mon, 02 May 2011 18:48:29 GMT</lp1:getlastmodified>
<lp1:getetag>"19f807a-719fc-4a24f782a5940"</lp1:getetag>
<lp3:executable>F</lp3:executable>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/dcs_server_simple_2_2_2.bit</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype/>
<lp1:creationdate>2011-08-19T19:59:06Z</lp1:creationdate>
<lp1:getcontentlength>169323</lp1:getcontentlength>
<lp1:getlastmodified>Tue, 19 Apr 2011 13:46:42 GMT</lp1:getlastmodified>
<lp1:getetag>"19f807b-2956b-4a145bcf79480"</lp1:getetag>
<lp3:executable>F</lp3:executable>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/vga_stripes_top_build_2.mcs</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype/>
<lp1:creationdate>2011-08-19T19:59:06Z</lp1:creationdate>
<lp1:getcontentlength>780476</lp1:getcontentlength>
<lp1:getlastmodified>Sun, 08 May 2011 16:35:20 GMT</lp1:getlastmodified>
<lp1:getetag>"19f807c-be8bc-4a2c64f082200"</lp1:getetag>
<lp3:executable>F</lp3:executable>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/dcs_pult_arm2_build_2.mcs</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype/>
<lp1:creationdate>2011-08-19T19:59:06Z</lp1:creationdate>
<lp1:getcontentlength>465404</lp1:getcontentlength>
<lp1:getlastmodified>Mon, 02 May 2011 18:14:32 GMT</lp1:getlastmodified>
<lp1:getetag>"19f807d-719fc-4a24efec03200"</lp1:getetag>
<lp3:executable>F</lp3:executable>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
<D:response xmlns:lp1="DAV:" xmlns:lp2="http://subversion.tigris.org/xmlns/dav/" xmlns:lp3="http://apache.org/dav/props/">
<D:href>/test/distout/rtl/top_ctrl_v4_build_0.bit</D:href>
<D:propstat>
<D:prop>
<lp1:resourcetype/>
<lp1:creationdate>2011-08-19T19:59:06Z</lp1:creationdate>
<lp1:getcontentlength>169294</lp1:getcontentlength>
<lp1:getlastmodified>Fri, 22 Jul 2011 17:44:22 GMT</lp1:getlastmodified>
<lp1:getetag>"19f807e-2954e-4a8ac04032980"</lp1:getetag>
<lp3:executable>F</lp3:executable>
<D:supportedlock>
<D:lockentry>
<D:lockscope><D:exclusive/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
<D:lockentry>
<D:lockscope><D:shared/></D:lockscope>
<D:locktype><D:write/></D:locktype>
</D:lockentry>
</D:supportedlock>
<D:lockdiscovery/>
</D:prop>
<D:status>HTTP/1.1 200 OK</D:status>
</D:propstat>
</D:response>
</D:multistatus>
'''
username, password = authenticate()
client = tinydav.WebDAVClient('cs.scircus.ru')
client.setbasicauth(username, password)
#response = client.propfind('/test/distout/rtl/jopa3',
#  depth = 1
#)

try:
  response = client.get('/test/distout/rtl/gh/')
except HTTPUserError as e:
  print e
  print 'No such file'
#response = client.put('/test/distout/rtl/jopa2',
#                      '111',
#                      "application/text")

print response
print response.statusline
print response.content
sys.exit()
#tree = etree.fromstring(response.content)
#html = etree.Element("response")
tree = etree.fromstring(t)
#nodes = tree.getchildren()
#for i in nodes:
#  print i.tag

def getn(node):
#    print node.tag
    if node.tag == '{DAV:}href':
      print node.text
    if node.tag == '{DAV:}resourcetype':
      folder = False
    if node.tag == '{DAV:}collection':
      folder = True
      print 'folder'
    for n in node:
        getn(n)
getn(tree.getroottree().getroot())

#print etree.tostring(tree)
#print response.content


