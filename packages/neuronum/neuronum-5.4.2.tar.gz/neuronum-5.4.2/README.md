<h1 align="center">
  <img src="https://neuronum.net/static/neuronum.svg" alt="Neuronum" width="100">
</h1>
<h4 align="center">Build, connect, and automate serverless data infrastructures with Neuronum</h4>

<p align="center">
  <a href="https://neuronum.net">
    <img src="https://img.shields.io/badge/Website-Neuronum-blue" alt="Website">
  </a>
  <a href="https://github.com/neuronumcybernetics/neuronum">
    <img src="https://img.shields.io/badge/Docs-Read%20now-green" alt="Documentation">
  </a>
  <img src="https://img.shields.io/badge/Version-5.4.0-blueviolet" alt="Lib Version">
  <img src="https://img.shields.io/badge/Python-3.9%2B-yellow" alt="Python Version">
</p>

---

## **Getting Started Goals**
- Learn about Neuronum
- Connect to Neuronum
- Build on Neuronum
- Interact with Neuronum


### **About Neuronum**
Neuronum is a framework to build serverless connected app & data gateways automating the processing and distribution of data transmission, storage, and streaming.


### **Features**
**Cell & Nodes**
- Cell: Account to connect and interact with Neuronum
- Nodes: Soft- and Hardware components hosting gateways

**Gateways**
- Transmitters (TX): Securely transmit and receive data packages
- Circuits (CTX): Store data in cloud-based key-value-label databases
- Streams (STX): Stream, synchronize, and control data in real time

#### Requirements
- Python >= 3.8 -> https://www.python.org/downloads/
- neuronum >= 5.4.0 -> https://pypi.org/project/neuronum/


------------------


### **Connect to Neuronum**
Installation
```sh
pip install neuronum                    # install neuronum dependencies
```

Create Cell:
```sh
neuronum create-cell                    # create Cell / Cell type / Cell network 
```

or

Connect Cell:
```sh
neuronum connect-cell                   # connect Cell
```

------------------


### **Build on Neuronum**
Initialize Node (app template):
```sh
neuronum init-node --app                # initialize a Node with app template
```

Change into Node folder
```sh
cd node_node_id                         # change directory
```

Start Node:
```sh
neuronum start-node                     # start Node
```

**Node Examples**
Visit: https://github.com/neuronumcybernetics/neuronum/tree/main/how_tos/nodes


------------------


### **Interact with Neuronum**
**Web-based**
1. Visit: https://neuronum.net
2. Connect your Cell
3. Explore Transmitters
4. Activate Transmitters

**Code-based**
```python
import asyncio
import neuronum

cell = neuronum.Cell(                                   # set Cell connection
    host="host",                                        # Cell host
    password="password",                                # Cell password
    network="neuronum.net",                             # Cell network -> neuronum.net
    synapse="synapse"                                   # Cell synapse
)

async def main():
                                                            
    TX = txID                                           # select the Transmitter TX
    data = {
        "say": "hello",
    }
    tx_response = await cell.activate_tx(TX, data)      # activate TX - > get response back
    print(tx_response)                                  # print Cell list
                                      
asyncio.run(main())
```

