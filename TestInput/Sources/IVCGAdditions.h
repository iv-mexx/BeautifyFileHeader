/**
 *  IVCGAdditions.h
 *  Polynom
 *
 *  Created by Markus Chmelar on 22.02.13.
 *  Copyright (c) 2013 TU Wien. All rights reserved.
 */

#ifndef Polynom_IVCGAdditions_h
#define Polynom_IVCGAdditions_h

// Macro that sets only the Position of a CGRect
#define CGRectSetPosition(r, x, y)      CGRectMake(x, y, r.size.width, r.size.height)
#define CGRectSetPositionX(r, x)        CGRectMake(x, r.origin.x, r.size.width, r.size.height)
#define CGRectSetPositionY(r, y)        CGRectMake(r.origin.y, y, r.size.width, r.size.height)
// Macro that sets only the Size of a CGRect
#define CGRectSetSize(r, width, height) CGRectMake(r.origin.x, r.origin.y, width, height)
#define CGRectSetHeight(r, height)      CGRectMake(r.origin.x, r.origin.y, r.size.width, height)
#define CGRectSetWidth(r, width)        CGRectMake(r.origin.x, r.origin.y, width, r.size.height)

#endif
