import h5py 
import numpy as np

from LarpixParser import event_parser as EvtParser
from LarpixParser import hit_parser as HitParser
#from LarpixParser import geom_dict_loader as DictLoader
from LarpixParser import util as util

switch_xz = True
detector = "ndlar"

f = h5py.File('../example_data/ndlar_ev20_larndsim.h5', 'r')
packets = f['packets'] # readout
G4_segments = f['tracks'] # Geant4 truth
assn = f['mc_packets_assn'] # G4-readout association


'''
    Loading LArPix geometry and run configuration
    Option 1: Use the default, the installed package data
              It's recommended, if you are not doing something unusual.
'''
run_config, geom_dict = util.detector_configuration(detector)

'''
    Loading LArPix geometry and run configuration
    Option 2: Point a pre-load LArPix geometry dictionary stored in a pickle file and a run configuration yaml file
'''
#geom_dict = util.load_geom_dict("../src/LarpixParser/config_repo/dict_repo/multi_tile_layout-3.0.40.pkl")

#run_config_path = '../src/LarpixParser/config_repo/ndlar-module.yaml'
#run_config = util.get_run_config(run_config_path)

'''
    Loading LArPix geometry and run configuration
    Option 3: Build a LArPix geometry dictionary on the fly and load a run configuration yaml file
'''
#from LarpixParser import geom_to_dict as DictBuilder
#geom_repo = '../src/LarpixParser/config_repo'
#larpix_layout_name = 'multi_tile_layout-3.0.40'
#geom_dict = DictBuilder.larpix_layout_to_dict(geom_repo, larpix_layout_name, save_dict=False)

#run_config_path = '../src/LarpixParser/config_repo/ndlar-module.yaml'
#run_config = util.get_run_config(run_config_path)

'''
    The following should be the read-out level information
    Since this package does not provide event parser, here, in the example we borrow the truth information
'''
ifspill = run_config['ifspill']
pckt_event_ids = EvtParser.packet_to_eventid(assn, G4_segments, ifspill)
event_ids = np.unique(pckt_event_ids[pckt_event_ids != -1]) 
t0_grp = EvtParser.get_t0(packets)

for i_ev, evt_id in enumerate(event_ids):

    #print("--------evt_id: ", evt_id)
    pckt_mask = pckt_event_ids == evt_id
    packets_ev = packets[pckt_mask]
    assn_ev = assn[pckt_mask]
    t0 = t0_grp[i_ev]
    
    ## x is the drift; y is the vertical direction; z is horizontal axis in pixel plane
    ## you can choose drift model by adding this to arguement "drift_model=1"
    #### 1: LArSoft suite 2: BNL mobility model

    # if you want position and energy (derived from the readout)
    x,y,z,dE = HitParser.hit_parser_energy(t0, packets_ev, geom_dict, run_config, switch_xz)

    # if you want position and charge [ke-]
    x,y,z,dQ = HitParser.hit_parser_charge(t0, packets_ev, geom_dict, run_config, switch_xz)

    # if you just want the position info
    x,y,z,t_drift = HitParser.hit_parser_position(t0, packets_ev, geom_dict, run_config, switch_xz)

    # if you want truth information together with the readout information
    # segID is a list of segments which contribute to the packet readout marked by the unique identification of true segments (tracks) per file
    # frac is the charge contribution per segment
    # pdg is the corresponding pdg code of the segment
    x,y,z,dQ,segID,frac,pdg = HitParser.hit_parser_charge_n_truth(t0, packets_ev, geom_dict, run_config, assn_ev, G4_segments, switch_xz)


