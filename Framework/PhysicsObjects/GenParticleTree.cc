class GenParticleTree
{
private:
	bool MatchParticleToString(GenParticleObj particle, std::string string){

	}

	std::vector<GenParticleObj> RunChain(GenParticleObj node, std::vector<std::string> chain) {

	}

public:
	GenParticleTree();
	~GenParticleTree();

	void AddParticle(GenParticleObj particle){

	}

	std::vector<GenParticleObj> GetChildren(GenParticleObj particle){

	}

	GenParticleObj GetParent(GenParticleObj particle){

	}

	

	std::vector<GenParticleObj> FindChain(std::string chainstring){

	}
	
};

class GenParticleObj
{
private:



	// Store an index for GenParticleTree parent or child
	void AddParent(int index){

	}
	void AddChild(int index){

	}

public:
	GenParticleObj(int index, );
	~GenParticleObj();
	
};