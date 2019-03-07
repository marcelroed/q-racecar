import abc


class Drawable:
    __metaclass__ = abc.ABCMeta

    def __lt__(self, other):
        return self.z_index < other.z_index

    @property
    @abc.abstractmethod
    def z_index(self):
        """Order of drawing, lowest first"""
        return

    @abc.abstractmethod
    def draw(self, surface, dt):
        """Draw self to surface using time step dt"""
        return


class Entity(Drawable):
    __metaclass__ = abc.ABCMeta

    @property
    def act_index(self):
        """Order of acting, lowerst first. Defaults to 0"""
        return 0

    @abc.abstractmethod
    def act(self, actions, dt):
        """Act based on actions and time step"""
