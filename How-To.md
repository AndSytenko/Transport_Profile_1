I. Create ring data files (yaml)

 1. input/
    a) resulted xlsx file (per region)
	    eg, ks-resulted-<reg>.xlsx
    b) Aggregation nodes data xls file
        eg, aggr-nodes.xlsx

 2. Convert xls data for a given ring into a yaml config
    a) For the whole region, with each ring config in a separate file:
    ./xl2ya2.py -r <path>/ks-resulted-<region>.xlsx -a <path>/aggr-nodes.xlsx -y <prefix}
    Eg,
    ./xl2ya2.py -r data/ode/input/ks-resulted-ode.xlsx -a data/ode/input/aggr-nodes.xlsx -i 3 -y out/ode1
    Will generate data 'yaml' files for the entire 'ODE' region from the 'ks-resulted-ode.xlsx' file.
    Resulted file are located in the 'out/' directory as ode1-ring<N>.yaml files , where N is a ring id.
    b) A yaml data file per ring:
    ./xl2ya2.py -r <path>/ks-resulted-<region>.xlsx -a <path>/aggr-nodes.xlsx -i <ring_id> -y <prefix}
    Eg. for ring # 3
    ./xl2ya2.py -r data/ode/input/ks-resulted-ode.xlsx -a data/ode/input/aggr-nodes.xlsx -i 3 -y out/ode1
    Will generate a data 'yaml' file for the ring #3 in the 'ODE' region from the 'ks-resulted-ode.xlsx' file.
    Resulted file is located in the 'out/' directory as ode1-ring3.yaml


II. Ring configuration (IP transport and all)

 1. Generate IXR nodes config

    a) 
   ./srcg.py -p <global-config> -c <ring-config> -t ds [-o <ixr-configs>]
     where, <global-config> - global configuration data
            <ring-config>   - config data for a specific ring 
            <ixr-configs>   - resulted config, optional, stdout - default
    Eg,  
    ./srcg.py -p conf/global.yaml -t ds -c out/ode1-ring14.yaml |./clksconf.sh > tmp/ode/ds.r14.cfg
        or
    ./srcg.py -p conf/global.yaml -t ds -c out/ode1-ring14.yaml -o tmp/ode/ds.r14.cfg && ./clksconf.sh tmp/ode/ds.r14.cfg 
 

 2. Generate Aggregation nodes (7750) config
    a)
   ./srcg.py -p <global-config> -c <ring-config> -t sr [-o <ixr-configs>]
    Similar to the IXR config generation

III. NFMP user config

./u4nsp.py -i <snmp_engine_id> -y <yaml_config>
    #-------------------------
    $ cat u4nsp.yaml
    snmpkey: /usr/bin/snmpkey
    snmpuser: 5620sam
    password: <snmp_passwd>
    #

    Eg,
    ./u4nsp.py -i 0000197f00001cc9ff000000 -y u4nsp.yaml
