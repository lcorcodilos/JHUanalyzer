// Subjet value lookup
namespace analyzer {
    float SubjetValLookup(int subjet_idx, ROOT::VecOps::RVec<Float_t> value_branch) {
        float score = value_branch[subjet_idx];

        // std::cout << subjet_idx1 << ", " << subjet_idx2 << std::endl;
        // if (subjet_idx > -1) {score = value_branch[subjet_idx];} // || subjet_idx >= value_branch.size()
        // else {score = -100;}

        return score;
    }
}
