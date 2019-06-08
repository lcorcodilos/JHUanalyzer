#####################################################################
# GenParticleChecker.py - Lucas Corcodilos 5/3/19                   #
# -----------------------------------------------                   #
# Class that takes in relevant gen particles, identifies            #
# relationships, and draws the tree for each event.                 #
# -----------------------------------------------                   #
# Prerequisites                                                     #
# -----------------------------------------------                   #
# * `pip install graphviz` -> python interface to graphiz           #
# * Download and install actual graphviz from here                  # 
#   https://graphviz.gitlab.io/_pages/Download/Download_source.html #
# * Will not work on CMSSW because of these dependencies            #
#####################################################################

import ROOT
from ROOT import TLorentzVector

class GenParticleTree:
    def __init__ (self):
        self.nodes = []
        # self.staged_nodes = []
        self.heads = []

    def AddParticle(self, mygenpart):
        self.staged_node = mygenpart
        # From old Update() which doesn't work
        # First check if current heads don't have new parents and remove them from heads if they do
        heads_to_delete = []
        for i, head in enumerate(self.heads):
            if head.motherIdx == self.staged_node.idx:
                heads_to_delete.append(i)
        for h in heads_to_delete:
            del self.heads[h]

        # Next identify staged node has no parent (heads)
        # If no parent, no other info we can get from this particle
        if self.staged_node.motherIdx not in [gpo.idx for gpo in self.nodes]:
            self.heads.append(self.staged_node)
            self.nodes.append(self.staged_node)

        # If parent, we can find parent and add staged node as the child to the parent
        else:
            for inode, node in enumerate(self.nodes):
                if self.staged_node.motherIdx == node.idx:
                    # print 'Print found edge '+ '%s, %s, %s' % (self.staged_node.name, self.staged_node.status, self.staged_node.motherIdx) + ' - '+ '%s, %s, %s' % (node.name, node.status, node.motherIdx)
                    self.staged_node.AddParent(inode)
                    node.AddChild(len(self.nodes))
                    self.nodes.append(self.staged_node)

    def GetParticles(self):
        return self.nodes

    def GetChildren(self,particle):
        children = []
        for i in particle.childIndex:
            children.append(self.nodes[i])
        return children

    def GetParents(self,particle):
        parents = []
        for i in particle.parentIndex:
            parents.append(self.nodes[i])
        return parents

    # def FindChain(self,chain): #chain is string of format 'A>B>C'
    #     particlenames_in_chain = [p.rstrip() for p in chain.split('>')]

    #     chains = [] # to be returned
    #     # Loop over all particles that could be the start of a chain
    #     for tree_particle in [n for n in self.nodes if n.name == particlenames_in_chain[0] or n.pdgId == particlenames_in_chain[0]]:
    #         cursor_position = 1 # Cursor at 1st position now (starting at 0 in line above)
    #         candidate_chain = [tree_particle] # Reinitialize chains to this new chain

    #         # While we haven't reached the end of the chain...
    #         while cursor_position < len(particlenames_in_chain):
    #             cursor_position += 1
    #             # Any children with same pdgId or name as current or previous chain item (allows for duplication of particles)
    #             next_particles = [self.nodes[i] for i in tree_particle.childIndex if (self.nodes[i].name == particlenames_in_chain[cursor_position]) or (self.nodes[i].pdgId == particlenames_in_chain[cursor_position]) or (self.nodes[i].name == particlenames_in_chain[cursor_position-1]) or (self.nodes[i].pdgId == particlenames_in_chain[cursor_position-1])] # Get the children

    #             # If no candidate children, move on
    #             if len(next_particles) < 1:
    #                 break
    #             elif len(next_particles) == 1:
    #                 candidate_chain.append(next_particles[0])
    #             else:
    #                 # Setup new chain which for multiple child particles of original looks like [[tree_particle,child1],[tree_particle,child2],..]
    #                 new_chain = []
    #                 for np in next_particles:
    #                     new_chain.append(candidate_chain+[np])
    #                 candidate_chain = new_chain


    #         # If we never covered the full chain (a break was called in the while loop above), try the next 0th particle
    #         if cursor_position < len(particlenames_in_chain)-1: 
    #             continue
    #         elif cursor_position == len(particlenames_in_chain)-1: # found a chain
    #             chains.append(candidate_chain)


    #     print chains


    def PrintTree(self,ievent,options=[]):  # final option is list of other attributes of GenParticleObj to draw
        from graphviz import Digraph
        dot = Digraph(comment='Particle tree for event '+str(ievent))
        for n in self.nodes:
            this_node_name = 'idx_'+str(n.idx)
            this_node_label = n.name
            # Build larger label if requested
            for o in options:
                if 'statusFlags' in o:
                    flag = o.split(':')[1]
                    this_node_label += '\n%s=%s'%(flag,n.statusFlags[flag])
                elif 'vect' in o:
                    kin = o.split(':')[1]
                    this_node_label += '\n%s=%s'%(kin,getattr(n.vect,kin)())
                else:
                    this_node_label += '\n%s=%s'%(o,getattr(n,o))

            dot.node(this_node_name, this_node_label)
            for ichild in n.childIndex:
                dot.edge(this_node_name, 'idx_'+str(self.nodes[ichild].idx))
        
        dot.render('particle_trees/test.gv',view=True)


class GenParticleObj:
    def __init__ (self, index, genpart):
        self.idx = index
        self.genpart = genpart
        self.status = genpart.status
        self.statusFlagsInt = genpart.statusFlags
        self.pdgId = genpart.pdgId
        self.name = ''
        self.vect = TLorentzVector()
        self.vect.SetPtEtaPhiM(genpart.pt,genpart.eta,genpart.phi,genpart.mass)
        self.pt = self.vect.Perp()
        self.eta = self.vect.Eta()
        self.phi = self.vect.Phi()
        self.mass = self.vect.M()
        self.motherIdx = genpart.genPartIdxMother

        self.statusFlags = {}

        # For GenParticleTree interface
        self.parentIndex = []
        self.childIndex = []

        self.Constants()
        self.SetStatusFlags()


    def Constants(self):
        self.GenParticleStatusFlags = {
            'isPrompt': 0,
            # 'isDecayedLeptonHadron': 1,
            # 'isTauDecayProduct': 2,
            # 'isPromptTauDecayProduct': 3,
            # 'isDirectTauDecayProduct': 4,
            # 'isDirectPromptTauDecayProduct': 5,
            # 'isDirectHadronDecayProduct': 6,
            'isHardProcess': 7,
            'fromHardProcess': 8,
            # 'isHardProcessTauDecayProduct': 9,
            # 'isDirectHardProcessTauDecayProduct': 10,
            'fromHardProcessBeforeFSR': 11,
            'isFirstCopy': 12,
            'isLastCopy': 13,
            'isLastCopyBeforeFSR': 14
        }
        self.PDGIds = {
            1:'d', 2:'u', 3:'s', 4:'c', 5:'b', 6:'t',
            11:'e', 12:'nu_e', 13:'mu', 14:'nu_mu', 15:'tau', 16:'nu_tau',
            21:'g', 22:'photon', 23:'Z', 24:'W', 25:'h'
        }

    # Compare to jet and do basic tests of proximity
    def CompareToJet(self,jetvect):
        sameHemisphere = True if self.vect.DeltaPhi(jetvect) < math.pi else False
        deltaR = self.vect.DeltaR() < 0.8
        deltaM = (abs(jetvect.M() - self.vect.M())/self.vect.M() < 0.05)

        return {'sameHemisphere':sameHemisphere,'deltaR':deltaR,'deltaM':deltaM}

    # Set individual flags
    def SetStatusFlags(self):
        for key in self.GenParticleStatusFlags.keys():
            self.statusFlags[key] = bitChecker(self.GenParticleStatusFlags[key], self.statusFlagsInt)

    def GetStatusFlag(self, flagName):
        return self.statusFlags[flagName]

    # Set name of particle (should come from PDG ID code)
    def SetPDGName(self,code):
        if code in self.PDGIds.keys():
            self.name = self.PDGIds[abs(code)]
        else:
            self.name = str(code)

    # Store an index for GenParticleTree parent
    def AddParent(self,index):
        self.parentIndex.append(index)

    def AddChild(self,index):
        self.childIndex.append(index)

# Evaluates bit stored in an integer
def bitChecker(bit, number):
    result = number & (1 << bit)
    if result > 0:
        return True
    else:
        return False

