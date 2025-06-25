import { Link, useNavigate } from "react-router-dom";
import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
} from "@/components/ui/navigation-menu";
import { auth } from "@/lib/api";
import { ModeToggle } from "@/components/mode-toggle";

const NavBar = () => {
  const navigate = useNavigate();
  const isAuthenticated = !!localStorage.getItem("authToken");

  const handleLogout = () => {
    auth.logout(navigate);
  };

  return (
    <nav className="border-b">
      <div className="container mx-auto px-4 py-3 flex items-center justify-between">
        {/* Left side */}
        <div className="flex items-center space-x-8">
          <Link to="/" className="text-xl font-bold">
            DORA Metrics
          </Link>
          <NavigationMenu>
            <NavigationMenuList className="flex space-x-4">
              <NavigationMenuItem>
                <NavigationMenuLink asChild>
                  <Link to="/" className="hover:text-primary">
                    Dashboard
                  </Link>
                </NavigationMenuLink>
              </NavigationMenuItem>
              <NavigationMenuItem>
                <NavigationMenuLink asChild>
                  <Link to="/releases" className="hover:text-primary">
                    Releases
                  </Link>
                </NavigationMenuLink>
              </NavigationMenuItem>
            </NavigationMenuList>
          </NavigationMenu>
        </div>

        {/* Right side */}
        <div className="flex items-center space-x-4">
          {isAuthenticated ? (
            <button
              onClick={handleLogout}
              className="hover:text-destructive"
            >
              Logout
            </button>
          ) : (
            <>
              <Link to="/login" className="hover:text-primary">
                Login
              </Link>
              <Link to="/register" className="hover:text-primary">
                Register
              </Link>
            </>
          )}
          <ModeToggle />
        </div>
      </div>
    </nav>
  );
};

export default NavBar;
