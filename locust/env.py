from .argument_parser import parse_options
from .event import Events
from .exception import RunnerAlreadyExistsError
from .stats import RequestStats
from .runners import LocalRunner, MasterRunner, WorkerRunner
from .web import WebUI


class Environment:
    events = None
    """
    Event hooks used by Locust internally, as well as to extend Locust's functionality
    See :ref:`events` for available events.
    """
    
    user_classes = []
    """User classes that the runner will run"""
    
    stats = None
    """Reference to RequestStats instance"""
    
    runner = None
    """Reference to the :class:`Runner <locust.runners.Runner>` instance"""
    
    web_ui = None
    """Reference to the WebUI instance"""
    
    host = None
    """Base URL of the target system"""
    
    reset_stats = False
    """Determines if stats should be reset once all simulated users have been spawned"""
    
    step_load = False
    """Determines if we're running in step load mode"""
    
    stop_timeout = None
    """
    If set, the runner will try to stop the runnning users gracefully and wait this many seconds 
    before killing them hard.
    """
    
    catch_exceptions = True
    """
    If True exceptions that happen within running users will be catched (and reported in UI/console).
    If False, exeptions will be raised.
    """

    parsed_options = parse_options(args=[])
    """Reference to the namespace that stores the parsed command line arguments"""
    
    def  __init__(
        self, *,
        user_classes=[],
        events=None, 
        host=None, 
        reset_stats=False, 
        step_load=False, 
        stop_timeout=None,
        catch_exceptions=True,
        parsed_options=parse_options(args=[]),
    ):
        if events:
            self.events = events
        else:
            self.events = Events()
        
        self.user_classes = user_classes
        self.stats = RequestStats()
        self.host = host
        self.reset_stats = reset_stats
        self.step_load = step_load
        self.stop_timeout = stop_timeout
        self.catch_exceptions = catch_exceptions
        self.parsed_options = parsed_options
    
    def _create_runner(self, runner_class, *args, **kwargs):
        if self.runner is not None:
            raise RunnerAlreadyExistsError("Environment.runner already exists (%s)" % self.runner)
        self.runner = runner_class(self, *args, **kwargs)
        return self.runner
    
    def create_local_runner(self):
        """
        Create a :class:`LocalRunner <locust.runners.LocalRunner>` instance for this Environment
        """
        return self._create_runner(LocalRunner)
        
    def create_master_runner(self, master_bind_host="*", master_bind_port=5557):
        """
        Create a :class:`MasterRunner <locust.runners.MasterRunner>` instance for this Environment
        
        :param master_bind_host: Interface/host that the master should use for incoming worker connections. 
                                 Defaults to "*" which means all interfaces.
        :param master_bind_port: Port that the master should listen for incoming worker connections on
        """
        return self._create_runner(
            MasterRunner,
            master_bind_host=master_bind_host,
            master_bind_port=master_bind_port,
        )
    
    def create_worker_runner(self, master_host, master_port):
        """
        Create a :class:`WorkerRunner <locust.runners.WorkerRunner>` instance for this Environment
        
        :param master_host: Host/IP of a running master node
        :param master_port: Port on master node to connect to
        """
        # Create a new RequestStats with use_response_times_cache set to False to save some memory
        # and CPU cycles, since the response_times_cache is not needed for Worker nodes
        self.stats = RequestStats(use_response_times_cache=False)
        return self._create_runner(
            WorkerRunner,
            master_host=master_host,
            master_port=master_port,
        )
    
    def create_web_ui(self, host="", port=8089, auth_credentials=None):
        """
        Creates a :class:`WebUI <locust.web.WebUI>` instance for this Environment and start running the web server
        
        :param host: Host/interface that the web server should accept connections to. Defaults to ""
                     which means all interfaces
        :param port: Port that the web server should listen to
        :param auth_credentials: If provided (in format "username:password") basic auth will be enabled
        """
        self.web_ui = WebUI(self, host, port, auth_credentials=auth_credentials)
        return self.web_ui
