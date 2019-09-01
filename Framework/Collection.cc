class Collection
{
private:
    std::string _prefix;
    int _lenVar;

public:
    Collection(std::string prefix, int lenVar){
        _prefix = prefix;
        _lenVar = lenVar;
    }
    ~Collection();
    
};