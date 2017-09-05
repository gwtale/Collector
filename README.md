<h1><strong>Installation</strong></h1>
<ol>
<li>In Zabbix server, create a proxy;</li>
<li>Assign the template <span class="css-truncate css-truncate-target">GTS-IS Sherlock for Ubuntu Xenial 16.04.xml to the proxy;</span></li>
<li><span class="css-truncate css-truncate-target">Fill in the macros in newly created proxy;</span></li>
</ol>
<p>&nbsp;</p>
<h1><span class="css-truncate css-truncate-target">How it works</span></h1>
<ol>
<li><span class="css-truncate css-truncate-target">Zabbix proxy connects to SoftLayer services via API;</span></li>
<li><span class="css-truncate css-truncate-target">Reads available devices and configurations;</span></li>
<li><span class="css-truncate css-truncate-target">Save data locally;</span></li>
<li><span class="css-truncate css-truncate-target">LLD items in "GTS-IS Sherlock for Ubuntu Xenial 16.04" will discover new devices from local file (created in item #3) and create hosts via Zabbix API. LLD will automatically assign templates and configure the hosts;</span></li>
<li><span class="css-truncate css-truncate-target">Zabbix proxy will connect to Softlayer SSL vpn </span></li>
</ol>
<p>&nbsp;</p>
<p>&nbsp;</p>
