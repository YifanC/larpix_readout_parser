import numpy as np
from sklearn.cluster import DBSCAN

def get_t0(packets, run_config):

    t0 = []
    pckts_t0 = packets[packets['packet_type'] == 7]['timestamp'] # external trigger # by default larnd-sim fills external trigger for each event

    pckts_t0_db = pckts_t0.reshape(-1,1)

    db = DBSCAN(eps=50, min_samples=2).fit(pckts_t0_db)
    labels = db.labels_
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    for i_ct in range(n_clusters_):
        ct_mask = labels == i_ct
        t0.append(np.min(pckts_t0[ct_mask]) * run_config['CLOCK_CYCLE'])

    t0 = np.array(t0)

    threshold = 40 #us
    t0_ev = np.delete(t0, np.argwhere(np.ediff1d(t0) <= threshold) + 1)

    return t0_ev

def get_t0_event(vertices, run_config, time_parser='t_event'):
    try:
        dt_window = run_config['beam_duration']
    except:
        dt_window = 0
        print("Found no 'beam_duration' in the configuration file")

    if time_parser in vertices.dtype.names and not (np.all(vertices[time_parser]) == 0):
        t0_ev = (np.unique(vertices[time_parser]) + dt_window *0.5)
    else:
        raise ValueError("True event time is not given!")

    return t0_ev

def packet_to_eventid(assn, tracks, event_parser='eventID'):
    '''
    Assoiciate packet to eventID.
    
    Arguments
    ---------
    assn : array_like
        packet to track association (`mc_packets_assn`) from `larnd-sim` output
        
    tracks: array_like
        list of track segments
        
    Returns
    -------
    event_ids: ndarray (N,)
        array of eventID.
        `len(event_ids)` equals to `len(packets)`
    '''
    track_ids = assn['track_ids'].max(axis=-1)

    event_ids = np.full_like(track_ids, -1, dtype=int)
    mask = track_ids != -1

    event_ids[mask] = tracks[event_parser][track_ids[mask]]
        
    return event_ids
