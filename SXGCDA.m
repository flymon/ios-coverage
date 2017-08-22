//
//  SXGCDA.m
//  Pods
//
//  Created by season-fly on 4/10/17.
//
//

#import "SXGCDA.h"

#import <AFNetworking/AFNetworking.h>

extern void __gcov_flush(void);

static inline NSString *GCDADirectoryPath(void) {
    NSString *documentDirectoryPath = NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, YES).firstObject;
    NSString *GCDADirectoryPath = [documentDirectoryPath stringByAppendingPathComponent:@"com.vipshop.spec.gcda"];
    if (![[NSFileManager defaultManager] fileExistsAtPath:GCDADirectoryPath]) {
        NSError *error;
        [[NSFileManager defaultManager] createDirectoryAtPath:GCDADirectoryPath
                                  withIntermediateDirectories:YES
                                                   attributes:nil
                                                        error:&error];
    }
    return GCDADirectoryPath;
}

static NSString * const kURLString = @"https://mobile.test.vipshop.com/mobilet/router.do";

@interface SXGCDA ()

@property (nonatomic, strong) AFHTTPSessionManager *sessionManager;
@property (nonatomic, strong) NSString *URLString;
@property (atomic, assign, getter=isReporting) BOOL reporting;

@end

@implementation SXGCDA

+ (instancetype)sharedInstance
{
    static SXGCDA *instance;
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        instance = [self new];
    });
    return instance;
}

- (instancetype)init
{
    self = [super init];
    if (self) {
        _sessionManager = ^() {
            AFHTTPSessionManager *manager = [AFHTTPSessionManager manager];
            manager.completionQueue = dispatch_queue_create("com.vipshop.gcda.session-manager.completion-queue", DISPATCH_QUEUE_SERIAL);
            manager.responseSerializer = [AFHTTPResponseSerializer serializer];
            manager.securityPolicy.allowInvalidCertificates = YES;
            manager.securityPolicy.validatesDomainName = NO;
            return manager;
        }();
        [self setupWithShortGitCommit:@"" UDID:@""];
    }
    return self;
}

- (void)setupWithShortGitCommit:(NSString *)shortGitCommit UDID:(NSString *)UDID
{
    if (!shortGitCommit || !UDID || self.isReporting) {
        return;
    }
    NSDictionary *queryParameters = @{
                                      @"service": @"iOSCodeCoverage.UploadFile",
                                      @"version": [NSBundle mainBundle].infoDictionary[@"CFBundleShortVersionString"],
                                      @"short_git_commit": shortGitCommit,
                                      @"udID": UDID
                                      };
    NSURLComponents *URLComponents = [NSURLComponents componentsWithString:kURLString];
    URLComponents.query = AFQueryStringFromParameters(queryParameters);
    self.URLString = URLComponents.URL.absoluteString;
}

- (void)reportGCDAWithFilePath:(NSString *)filePath
                       completion:(void (^)(NSError *error))completion

{
    [self.sessionManager POST:self.URLString parameters:nil constructingBodyWithBlock:^(id<AFMultipartFormData>  _Nonnull formData) {
        [formData appendPartWithFileURL:[NSURL fileURLWithPath:filePath] name:@"file" error:NULL];
    } progress:NULL  success:^(NSURLSessionDataTask * _Nonnull task, id  _Nullable responseObject) {
        completion(nil);
    } failure:^(NSURLSessionDataTask * _Nullable task, NSError * _Nonnull error) {
        completion(error);
    }];
}

- (void)reportGCDACompletion:(void (^)(NSError *error))completion
{
    if (self.isReporting) {
        return;
    }
    
    self.reporting = YES;
    
    dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0), ^{
        NSError * __block groupError;

        [[NSFileManager defaultManager] removeItemAtPath:GCDADirectoryPath() error:&groupError];
        NSString *directoryPath = GCDADirectoryPath();
        setenv("GCOV_PREFIX", [directoryPath cStringUsingEncoding:NSUTF8StringEncoding], 1);
        setenv("GCOV_PREFIX_STRIP", "13", 1);
        __gcov_flush();
        
        dispatch_group_t group = dispatch_group_create();

        NSArray<NSString *> *subpathArray = [[NSFileManager defaultManager] subpathsOfDirectoryAtPath:directoryPath error:&groupError];
        for (NSString *subpath in subpathArray) {
            if ([subpath.pathExtension isEqualToString:@"gcda"]) {
                NSString *filePath = [directoryPath stringByAppendingPathComponent:subpath];
                dispatch_group_enter(group);
                [self reportGCDAWithFilePath:filePath completion:^(NSError *error) {
                    groupError = error;
                    dispatch_group_leave(group);
                }];
            }
        }
        
        dispatch_group_wait(group, DISPATCH_TIME_FOREVER);
        self.reporting = NO;
        if (completion) {
            dispatch_async(dispatch_get_main_queue(), ^{
                completion(groupError);
            });
        }
    });
}

@end
