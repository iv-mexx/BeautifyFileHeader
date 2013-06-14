//
//  LocalizationHandlerUtil.h
//  Polynom
//
//  Created by Markus Chmelar on 12.12.12.
//  Copyright (c) 2012 TU Wien. All rights reserved.
//

#import <Foundation/Foundation.h>

@interface LocalizationHandlerUtil : NSObject
/**
 *	@brief		Get the Singleton Instance
 */
+ (LocalizationHandlerUtil *)sharedLocalizationHandlerUtil;

- (NSString *)localizedString:(NSString *)key comment:(NSString *)comment;
@end
