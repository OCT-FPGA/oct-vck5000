"""OCT VCK5000 profile with post-boot script.
"""

# Import the Portal object.
import geni.portal as portal
# Import the ProtoGENI library.


# Import the Portal object.
import geni.portal as portal
# Import the ProtoGENI library.
import geni.rspec.pg as pg
# We use the URN library below.
import geni.urn as urn
# Emulab extension
import geni.rspec.emulab

# Create a portal context.
pc = portal.Context()

# Create a Request object to start building the RSpec.
request = pc.makeRequestRSpec()

# Pick your image.
imageList = [('urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU20-64-STD', 'UBUNTU 20.04'),
             ('urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU22-64-STD', 'UBUNTU 22.04')] 

dockerImageList = [('pytorch')]
workflow = ['Vitis', 'Vitis-AI', 'CUDA']
toolVersion = ['2023.1'] 

pc.defineParameter("nodes","List of nodes",
                   portal.ParameterType.STRING,"",
                   longDescription="Comma-separated list of nodes (e.g., pc176,pc177). Please check the list of available nodes within the Mass cluster at https://www.cloudlab.us/cluster-status.php before you specify the nodes.")
                 
pc.defineParameter("workflow", "Workflow",
                   portal.ParameterType.STRING,
                   workflow[0], workflow,
                   longDescription="Use either Vitis or Vitis-AI.")   

pc.defineParameter("toolVersion", "Tool Version",
                   portal.ParameterType.STRING,
                   toolVersion[0], toolVersion,
                   longDescription="Select a tool version (only applicable for Vitis flow).")   

pc.defineParameter("osImage", "Select Image",
                   portal.ParameterType.IMAGE,
                   imageList[0], imageList,
                   longDescription="Supported operating systems are Ubuntu and CentOS.")    

pc.defineParameter("dockerImage", "Docker Image",
                   portal.ParameterType.STRING,
                   dockerImageList[0], dockerImageList,
                   longDescription="Supported docker images (only applicable for Vitis-AI flow).")  

# Retrieve the values the user specifies during instantiation.
params = pc.bindParameters()        

# Check parameter validity.
  
pc.verifyParameters()

lan = request.LAN()

nodeList = params.nodes.split(',')

# Process nodes, adding to FPGA network
i = 0
for nodeName in nodeList:
    host = request.RawPC(nodeName)
    # UMass cluster
    bs = host.Blockstore("bs", "/mydata")
    bs.size = "80GB"
    host.component_manager_id = "urn:publicid:IDN+cloudlab.umass.edu+authority+cm"
    # Assign to the node hosting the FPGA.
    host.component_id = nodeName
    host.disk_image = params.osImage

    if params.workflow == 'Vitis':
        host.addService(pg.Execute(shell="bash", command="sudo /local/repository/post-boot-vitis.sh " + params.toolVersion + "  >> /local/logs/output_log.txt"))
    elif params.workflow == 'Vitis-AI':  
        host.addService(pg.Execute(shell="bash", command="sudo /local/repository/post-boot-vitis-ai.sh " + params.dockerImage + " >> /local/logs/output_log.txt"))
    elif params.workflow == 'CUDA':  
        host.addService(pg.Execute(shell="bash", command="sudo /local/repository/post-boot-cuda.sh  >> /local/logs/output_log.txt"))  
    # Since we want to create network links to the FPGA, it has its own identity.
    #fpga = request.RawPC("fpga-" + nodeName)
    # UMass cluster
    #fpga.component_manager_id = "urn:publicid:IDN+cloudlab.umass.edu+authority+cm"
    # Assign to the fgpa node
    #fpga.component_id = "fpga-" + nodeName
    # Use the default image for the type of the node selected. 
    #fpga.setUseTypeDefaultImage()

    # Secret sauce.
    #fpga.SubNodeOf(host)

    host_iface1 = host.addInterface()
    host_iface1.component_id = "eth2"
    host_iface1.addAddress(pg.IPv4Address("192.168.40." + str(i+30), "255.255.255.0")) 
    #fpga_iface1 = fpga.addInterface()
    #fpga_iface1.component_id = "eth0"
    #fpga_iface1.addAddress(pg.IPv4Address("192.168.40." + str(i+10), "255.255.255.0"))
    #fpga_iface2 = fpga.addInterface()
    #fpga_iface2.component_id = "eth1"
    #fpga_iface2.addAddress(pg.IPv4Address("192.168.40." + str(i+20), "255.255.255.0"))
    
    #lan.addInterface(fpga_iface1)
    #lan.addInterface(fpga_iface2)
    #lan.addInterface(host_iface1)
  
    i+=1

pc.printRequestRSpec(request)
