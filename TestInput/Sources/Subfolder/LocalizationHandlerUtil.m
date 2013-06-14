//
//  LocalizationHandlerUtil.m
//  Polynom
//
//  Created by Markus Chmelar on 12.12.12.
//  Copyright (c) 2012 TU Wien. All rights reserved.
//

#import "LocalizationHandlerUtil.h"
#import "Singleton_GCD_Macro.h"
@implementation LocalizationHandlerUtil

SINGLETON_GCD(LocalizationHandlerUtil);

- (NSString *)localizedString:(NSString *)key comment:(NSString *)comment
{
	// default localized string loading
	NSString *localizedString = [[NSBundle mainBundle] localizedStringForKey:key value:key table:nil];

	// if (value == key) and comment is not nil -> returns comment
	if([localizedString isEqualToString:key] && comment != nil)
		return comment;

	return localizedString;
}

@end
