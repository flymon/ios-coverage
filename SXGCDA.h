//
//  SXGCDA.h
//  Pods
//
//  Created by season-fly  on 4/10/17.
//
//

#import <Foundation/Foundation.h>

@interface SXGCDA : NSObject

+ (instancetype)sharedInstance;

- (void)setupWithShortGitCommit:(NSString *)shortGitCommit UDID:(NSString *)UDID;

- (void)reportGCDACompletion:(void (^)(NSError *error))completion;

@end
