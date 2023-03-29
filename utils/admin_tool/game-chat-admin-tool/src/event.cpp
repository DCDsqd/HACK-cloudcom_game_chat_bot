#include "event.h"

Event::Event()
{

}

Event::~Event()
{

}

EventPlacementData::EventPlacementData()
{

}

EventPlacementData::~EventPlacementData()
{

}

EventPlacementData::EventPlacementData(int idx_, size_t h_, size_t w_) : idx(idx_), h(h_), w(w_)
{
    sz = {int(h_), int(w_)};
}
